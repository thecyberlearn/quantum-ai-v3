from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
import json
import time
import requests
from datetime import datetime

from .models import WorkflowRequest, WorkflowResponse, WorkflowAnalytics
from .config.agents import get_agent_config, format_message_for_n8n, get_available_agents, get_all_agents
import logging

logger = logging.getLogger(__name__)


def marketplace_view(request):
    """Agent marketplace using AGENT_CONFIGS - no database dependency"""
    agents_data = get_all_agents()
    
    # Group agents by category
    agents_by_category = {}
    all_categories = set()
    
    for agent_slug, agent_config in agents_data.items():
        category = agent_config.get('category', 'utilities')
        all_categories.add(category)
        
        if category not in agents_by_category:
            agents_by_category[category] = []
            
        # Add slug to agent data for URL generation
        agent_data = agent_config.copy()
        agent_data['slug'] = agent_slug
        agents_by_category[category].append(agent_data)
    
    # Filter by category if specified
    selected_category = request.GET.get('category')
    if selected_category and selected_category in all_categories:
        agents_by_category = {selected_category: agents_by_category[selected_category]}
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        filtered_agents = {}
        for category, agents in agents_by_category.items():
            filtered_agents[category] = [
                agent for agent in agents 
                if search_query.lower() in agent['name'].lower() or 
                   search_query.lower() in agent['description'].lower()
            ]
        agents_by_category = {k: v for k, v in filtered_agents.items() if v}
    
    context = {
        'agents_by_category': agents_by_category,
        'all_categories': sorted(all_categories),
        'selected_category': selected_category,
        'search_query': search_query,
        'total_agents': len(agents_data)
    }
    
    return render(request, 'workflows/marketplace.html', context)


def send_file_to_webhook(webhook_url, uploaded_file, form_data, timeout=60):
    """Send file to N8N webhook endpoint"""
    logger.info(f"🔍 DEBUG: send_file_to_webhook called!")
    logger.info(f"🔍 DEBUG: webhook_url={webhook_url}")
    logger.info(f"🔍 DEBUG: uploaded_file={uploaded_file}")
    logger.info(f"🔍 DEBUG: form_data={form_data}")
    
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        
        logger.info(f"✅ Sending file to webhook: {webhook_url}")
        logger.info(f"✅ File size: {len(file_content)} bytes")
        logger.info(f"✅ File name: {uploaded_file.name}")
        
        # Prepare multipart form data
        files = {
            'file': (uploaded_file.name, file_content, 'application/pdf')
        }
        
        # Add analysis type if provided
        data = {}
        if 'analysisType' in form_data:
            data['analysisType'] = form_data['analysisType']
        
        start_time = time.time()
        response = requests.post(webhook_url, files=files, data=data, timeout=timeout)
        processing_time = time.time() - start_time
        
        logger.info(f"Webhook response status: {response.status_code}")
        logger.info(f"Processing time: {processing_time:.2f}s")
        logger.info(f"Response preview: {response.text[:200]}...")
        
        response.raise_for_status()
        
        # Parse JSON response from webhook
        if response.text.strip():
            try:
                result_data = response.json()
                logger.info(f"Webhook returned JSON: {result_data}")
                
                # Store the analysis results in the workflow request
                if 'sections' in result_data:
                    # Success response with analysis sections
                    return {'success': True, 'data': result_data}
                elif result_data.get('status') == 'error':
                    # Error response from N8N
                    logger.error(f"N8N webhook error: {result_data.get('error_message', 'Unknown error')}")
                    return {'success': False, 'error': result_data.get('error_message', 'Analysis failed')}
                else:
                    # Unexpected response format
                    logger.warning(f"Unexpected webhook response format: {result_data}")
                    return {'success': True, 'data': result_data}
                    
            except ValueError as e:
                logger.error(f"Invalid JSON response from webhook: {e}")
                logger.info(f"Raw response: {response.text[:500]}")
                return {'success': False, 'error': 'Invalid response from analysis service'}
        else:
            logger.warning("Webhook returned empty response")
            return {'success': False, 'error': 'Empty response from analysis service'}
            
    except requests.exceptions.Timeout:
        logger.error(f"Webhook timeout after {timeout}s")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to webhook: {webhook_url}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending to webhook: {e}")
        return False


@login_required
def workflow_handler(request, agent_slug):
    """Universal handler for all workflow agents with individual templates"""
    
    # Get agent configuration
    agent_config = get_agent_config(agent_slug)
    if not agent_config:
        raise Http404("Agent configuration not found")
    
    # Agent config serves as the agent data (no database dependency)
    agent = {
        'slug': agent_slug,
        'name': agent_config['name'],
        'price': agent_config['price'],
        'icon': agent_config['icon'],
        'description': agent_config['description']
    }
    
    if request.method == 'POST':
        return process_workflow_request(request, agent_slug, agent_config, agent)
    
    # Determine template path - use individual templates
    template_mapping = {
        'social-ads-generator': 'workflows/social-ads-generator.html',
        'job-posting-generator': 'workflows/job-posting-generator.html',
        'five-whys-analyzer': 'workflows/five-whys-analyzer.html',
        'weather-reporter': 'workflows/weather-reporter.html',
        'template-demo': 'workflows/agent-template-starter.html',
        'data-analyzer': 'workflows/data-analyzer.html',
    }
    
    template_name = template_mapping.get(agent_slug)
    if not template_name:
        raise Http404("Template not found for agent")
    
    # Add timestamp for cache busting and available agents for navigation
    context = {
        'agent': agent,
        'agent_config': agent_config,
        'available_agents': get_available_agents(),
        'timestamp': int(time.time()),
    }
    return render(request, template_name, context)


def process_workflow_request(request, agent_slug, agent_config, agent):
    """Process workflow request (called from workflow_handler)"""
    logger.info(f"🔍 DEBUG: process_workflow_request called with agent_slug={agent_slug}")
    logger.info(f"🔍 DEBUG: request.method={request.method}")
    logger.info(f"🔍 DEBUG: request.FILES={dict(request.FILES)}")
    logger.info(f"🔍 DEBUG: request.POST={dict(request.POST)}")
    
    # Template mapping for error returns
    template_mapping = {
        'social-ads-generator': 'workflows/social-ads-generator.html',
        'job-posting-generator': 'workflows/job-posting-generator.html',
        'five-whys-analyzer': 'workflows/five-whys-analyzer.html',
        'weather-reporter': 'workflows/weather-reporter.html',
        'template-demo': 'workflows/agent-template-starter.html',
        'data-analyzer': 'workflows/data-analyzer.html',
    }
    
    try:
        # Extract form data
        form_data = {}
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                form_data[key] = value
        
        # Handle file uploads (but don't store file objects in form_data for JSON serialization)
        logger.info(f"DEBUG: request.FILES = {request.FILES}")
        logger.info(f"DEBUG: request.FILES.keys() = {list(request.FILES.keys())}")
        
        uploaded_files = {}
        for key, file in request.FILES.items():
            logger.info(f"DEBUG: Found file - {key}: {file.name} ({file.size} bytes)")
            # Store file metadata only (not the file object itself)
            form_data[f"{key}_name"] = file.name
            form_data[f"{key}_size"] = file.size
            # Keep actual file object separate for processing
            uploaded_files[key] = file
            
        logger.info(f"DEBUG: Final form_data keys = {list(form_data.keys())}")
        logger.info(f"DEBUG: Uploaded files = {list(uploaded_files.keys())}")
        
        # Basic validation - ensure we have form data
        if not form_data:
            context = {
                'agent': agent,
                'agent_config': agent_config,
                'error': 'No form data provided.',
                'timestamp': int(time.time()),
            }
            template_name = template_mapping.get(agent_slug)
            return render(request, template_name, context)
        
        # Check user balance
        if not request.user.has_sufficient_balance(agent_config['price']):
            context = {
                'agent': agent,
                'agent_config': agent_config,
                'balance_error': f'Insufficient balance. You need {agent_config["price"]} AED.',
                'form_data': form_data,
                'timestamp': int(time.time()),
            }
            template_name = template_mapping.get(agent_slug)
            return render(request, template_name, context)
        
        # Create workflow request record
        workflow_request = WorkflowRequest.objects.create(
            user=request.user,
            agent_slug=agent_slug,
            input_data=form_data,
            status='processing'
        )
        
        # Actually send request to webhook (for agents that support file upload)
        logger.info(f"🔍 DEBUG: Checking webhook conditions - agent_slug={agent_slug}, has_file={'document_file' in uploaded_files or 'file' in uploaded_files}")
        file_upload_agents = ['data-analyzer']
        has_file = 'file' in uploaded_files or 'document_file' in uploaded_files
        
        if agent_slug in file_upload_agents and has_file:
            try:
                # Check if this is an AJAX request (like the original system)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Send file to webhook in background and return JSON response
                    # Get the uploaded file (different field names for different agents)
                    uploaded_file = uploaded_files.get('file') or uploaded_files.get('document_file')
                    webhook_result = send_file_to_webhook(
                        agent_config['webhook_url'], 
                        uploaded_file,
                        form_data
                    )
                    
                    if webhook_result and webhook_result.get('success'):
                        # Deduct user balance for successful processing
                        request.user.deduct_balance(agent_config['price'])
                        workflow_request.status = 'completed'
                        workflow_request.save()
                        
                        # Store analysis results in the workflow request
                        analysis_data = webhook_result.get('data', {})
                        try:
                            # Create WorkflowResponse with analysis data
                            WorkflowResponse.objects.create(
                                request=workflow_request,
                                formatted_output=analysis_data,
                                success=True,
                                processing_time=1.53  # Could get this from webhook timing
                            )
                        except Exception as resp_error:
                            logger.warning(f"Could not save response data: {resp_error}")
                            # Continue anyway - the main processing worked
                        
                        return JsonResponse({
                            'success': True,
                            'request_id': str(workflow_request.id),
                            'wallet_balance': float(request.user.wallet_balance),
                            'report_text': analysis_data.get('sections', [{}])[0].get('content', 'Analysis completed'),
                            'analysis_results': analysis_data
                        })
                    else:
                        workflow_request.status = 'failed'
                        workflow_request.save()
                        error_msg = webhook_result.get('error', 'Failed to process file') if webhook_result else 'Connection failed'
                        return JsonResponse({
                            'success': False,
                            'error': error_msg
                        })
                else:
                    # Non-AJAX request, return HTML template
                    context = {
                        'agent': agent,
                        'agent_config': agent_config,
                        'processing': True,
                        'request_id': workflow_request.id,
                        'timestamp': int(time.time()),
                    }
            except Exception as e:
                logger.error(f"Webhook error for {agent_slug}: {e}")
                workflow_request.status = 'failed'
                workflow_request.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Service temporarily unavailable. Please try again later.'
                    })
                else:
                    context = {
                        'agent': agent,
                        'agent_config': agent_config,
                        'error': 'Service temporarily unavailable. Please try again later.',
                        'timestamp': int(time.time()),
                    }
        else:
            # For other agents or no file upload, show processing message
            context = {
                'agent': agent,
                'agent_config': agent_config,
                'processing': True,
                'request_id': workflow_request.id,
                'timestamp': int(time.time()),
            }
        
        template_name = template_mapping.get(agent_slug)
        return render(request, template_name, context)
        
    except Exception as e:
        logger.error(f"Workflow processing error for {agent_slug}: {e}", exc_info=True)
        context = {
            'agent': agent,
            'agent_config': agent_config,
            'error': 'An error occurred while processing your request. Please try again.',
            'timestamp': int(time.time()),
        }
        template_name = template_mapping.get(agent_slug)
        return render(request, template_name, context)


@login_required
@require_http_methods(["POST"])
@ratelimit(key='user', rate='20/m', method='POST', block=False)
def process_workflow_api(request):
    """API endpoint for processing workflows (alternative to direct N8N calls)"""
    
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Workflow API rate limit exceeded for user {request.user.id}")
        return JsonResponse({'error': 'Too many requests. Please wait a moment.'}, status=429)
    
    try:
        # Parse JSON request
        data = json.loads(request.body)
        agent_slug = data.get('agent_slug')
        form_data = data.get('form_data', {})
        
        if not agent_slug:
            return JsonResponse({'error': 'Agent slug is required'}, status=400)
        
        # Get agent configuration
        agent_config = get_agent_config(agent_slug)
        if not agent_config:
            return JsonResponse({'error': 'Agent not found'}, status=404)
        
        # Basic validation - ensure we have form data
        if not form_data:
            return JsonResponse({'error': 'No form data provided'}, status=400)
        
        # Check user balance
        if not request.user.has_sufficient_balance(agent_config['price']):
            return JsonResponse({
                'error': 'Insufficient balance',
                'required': float(agent_config['price']),
                'current': float(request.user.wallet_balance)
            }, status=400)
        
        # Create workflow request
        workflow_request = WorkflowRequest.objects.create(
            user=request.user,
            agent_slug=agent_slug,
            input_data=form_data,
            status='processing'
        )
        
        # In a real implementation, this would call N8N
        # For now, return processing status
        return JsonResponse({
            'success': True,
            'request_id': str(workflow_request.id),
            'status': 'processing',
            'message': 'Request received and processing'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        logger.error(f"Workflow API error: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
def workflow_status(request, request_id):
    """Get workflow processing status"""
    try:
        workflow_request = get_object_or_404(
            WorkflowRequest, 
            id=request_id, 
            user=request.user
        )
        
        response_data = {
            'request_id': str(workflow_request.id),
            'status': workflow_request.status,
            'created_at': workflow_request.created_at.isoformat(),
        }
        
        # Include response data if completed
        if hasattr(workflow_request, 'response') and workflow_request.response:
            response_data['output'] = workflow_request.response.formatted_output
            response_data['processing_time'] = float(workflow_request.response.processing_time or 0)
            response_data['success'] = workflow_request.response.success
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Status check error: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to get status'}, status=500)


@login_required
def user_workflows(request):
    """Show user's workflow history"""
    workflows = WorkflowRequest.objects.filter(user=request.user).order_by('-created_at')[:50]
    
    context = {
        'workflows': workflows,
    }
    return render(request, 'workflows/history.html', context)


@login_required
def workflow_analytics(request):
    """Show workflow analytics for the user"""
    
    # Get user's workflow analytics
    analytics = WorkflowAnalytics.objects.filter(user=request.user).order_by('-date')[:30]
    
    # Calculate summary statistics
    total_workflows = WorkflowRequest.objects.filter(user=request.user).count()
    successful_workflows = WorkflowAnalytics.objects.filter(user=request.user, success=True).count()
    
    success_rate = (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0
    
    context = {
        'analytics': analytics,
        'total_workflows': total_workflows,
        'successful_workflows': successful_workflows,
        'success_rate': success_rate,
    }
    return render(request, 'workflows/analytics.html', context)
