from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
import json
import time
from datetime import datetime

from agent_base.models import BaseAgent
from .models import WorkflowRequest, WorkflowResponse, WorkflowAnalytics
from .config.agents import get_agent_config, format_message_for_n8n, get_available_agents
import logging

logger = logging.getLogger(__name__)


@login_required
def workflow_handler(request, agent_slug):
    """Universal handler for all workflow agents with individual templates"""
    
    # Get agent configuration
    agent_config = get_agent_config(agent_slug)
    if not agent_config:
        raise Http404("Agent configuration not found")
    
    # Get agent from BaseAgent model
    try:
        agent = BaseAgent.objects.get(slug=agent_slug, is_active=True)
    except BaseAgent.DoesNotExist:
        raise Http404("Agent not found")
    
    if request.method == 'POST':
        return process_workflow_request(request, agent_slug, agent_config, agent)
    
    # Determine template path - use individual templates
    template_mapping = {
        'social-ads-generator': 'workflows/social-ads-generator.html',
        'data-analyzer': 'workflows/data-analyzer.html', 
        'job-posting-generator': 'workflows/job-posting-generator.html',
        'five-whys-analyzer': 'workflows/five-whys-analyzer.html',
        'weather-reporter': 'workflows/weather-reporter.html',
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
    # Template mapping for error returns
    template_mapping = {
        'social-ads-generator': 'workflows/social-ads-generator.html',
        'data-analyzer': 'workflows/data-analyzer.html', 
        'job-posting-generator': 'workflows/job-posting-generator.html',
        'five-whys-analyzer': 'workflows/five-whys-analyzer.html',
        'weather-reporter': 'workflows/weather-reporter.html',
    }
    
    try:
        # Extract form data
        form_data = {}
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                form_data[key] = value
        
        # Handle file uploads
        for key, file in request.FILES.items():
            form_data[key] = file
        
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
        
        # For now, show processing message (actual N8N integration happens via JavaScript)
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
