from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import DataAnalysisAgentRequest, DataAnalysisAgentResponse
from .processor import DataAnalysisAgentProcessor
import json


@login_required
def data_analyzer_detail(request):
    """Detail page for Data Analysis Agent agent"""
    try:
        agent = BaseAgent.objects.get(slug='data-analyzer')
    except BaseAgent.DoesNotExist:
        messages.error(request, 'Data Analysis Agent agent not found.')
        return redirect('core:homepage')
    
    # Handle AJAX POST requests for processing
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Handle multipart form data for file uploads
            data = request.POST.dict()
            files = request.FILES
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Validate file upload
            data_file = files.get('file')
            if not data_file:
                return JsonResponse({'error': 'Data file is required'}, status=400)
            
            # Create request object (no wallet deduction yet - only after successful processing)
            agent_request = DataAnalysisAgentRequest.objects.create(
                user=request.user,
                agent=agent,
                cost=agent.price,
                data_file=data_file,
                analysis_type=data.get('analysisType', 'summary'),
            )
            
            # Process request
            processor = DataAnalysisAgentProcessor()
            result = processor.process_request(
                request_obj=agent_request,
                user_id=request.user.id,
                data_file_url=agent_request.data_file.url if agent_request.data_file else '',
                analysis_type=data.get('analysisType', 'summary'),
            )
            
            # Refresh user from database to get updated wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'request_id': str(agent_request.id),
                'message': 'Data analysis request processed successfully',
                'wallet_balance': float(request.user.wallet_balance)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # Handle non-AJAX POST requests (redirect to prevent resubmission popup)
    elif request.method == 'POST':
        messages.info(request, 'Please use the analyze button to process your data.')
        return redirect('data_analyzer:detail')
    
    # Regular GET request - show the form page
    user_requests = DataAnalysisAgentRequest.objects.filter(
        user=request.user
    ).select_related('agent').prefetch_related('response').order_by('-created_at')[:10]
    
    # Get other available agents for quick access
    available_agents = BaseAgent.objects.filter(
        is_active=True
    ).exclude(slug='data-analyzer').order_by('name')
    
    context = {
        'agent': agent,
        'user_requests': user_requests,
        'available_agents': available_agents
    }
    return render(request, 'data_analyzer/detail.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class DataAnalysisAgentProcessView(View):
    """Process Data Analysis Agent requests"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Handle multipart form data for file uploads
            data = request.POST.dict()
            files = request.FILES
            
            # Get agent
            agent = BaseAgent.objects.get(slug='data-analyzer')
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Validate file upload
            data_file = files.get('file')
            if not data_file:
                return JsonResponse({'error': 'PDF file is required'}, status=400)
            
            # Create request object (no wallet deduction yet - only after successful processing)
            agent_request = DataAnalysisAgentRequest.objects.create(
                user=request.user,
                agent=agent,
                cost=agent.price,
                data_file=data_file,
                analysis_type=data.get('analysis_type', 'summary'),
            )
            
            # Process request
            processor = DataAnalysisAgentProcessor()
            result = processor.process_request(
                request_obj=agent_request,
                user_id=request.user.id,
                data_file_url=agent_request.data_file.url if agent_request.data_file else '',
                analysis_type=data.get('analysis_type', 'summary'),
            )
            
            # Refresh user from database to get updated wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'request_id': str(agent_request.id),
                'message': 'Data Analysis Agent request processed successfully',
                'wallet_balance': float(request.user.wallet_balance)
            })
            
        except BaseAgent.DoesNotExist:
            return JsonResponse({'error': 'Data Analysis Agent agent not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def data_analyzer_status(request, request_id):
    """Get status for a specific request (for polling)"""
    try:
        agent_request = DataAnalysisAgentRequest.objects.get(
            id=request_id,
            user=request.user
        )
        
        if hasattr(agent_request, 'response'):
            response = agent_request.response
            # Refresh user to get current wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': response.success,
                'status': agent_request.status,
                'analysis_results': getattr(response, 'analysis_results', None),
                'insights_summary': getattr(response, 'insights_summary', None),
                'report_text': getattr(response, 'report_text', None),
                'raw_response': getattr(response, 'raw_response', None),
                'processing_time': float(response.processing_time) if response.processing_time else None,
                'error_message': response.error_message,
                'wallet_balance': float(request.user.wallet_balance)
            })
        else:
            return JsonResponse({
                'success': False,
                'status': agent_request.status,
                'message': 'Processing in progress...'
            })
            
    except DataAnalysisAgentRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def data_analyzer_result(request, request_id):
    """Get result for a specific request"""
    try:
        agent_request = DataAnalysisAgentRequest.objects.get(
            id=request_id,
            user=request.user
        )
        
        if hasattr(agent_request, 'response'):
            response = agent_request.response
            # Refresh user to get current wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': response.success,
                'status': agent_request.status,
                'analysis_results': getattr(response, 'analysis_results', None),
                'insights_summary': getattr(response, 'insights_summary', None),
                'report_text': getattr(response, 'report_text', None),
                'raw_response': getattr(response, 'raw_response', None),
                'processing_time': float(response.processing_time) if response.processing_time else None,
                'error_message': response.error_message,
                'wallet_balance': float(request.user.wallet_balance)
            })
        else:
            return JsonResponse({
                'success': False,
                'status': agent_request.status,
                'message': 'Processing in progress...'
            })
            
    except DataAnalysisAgentRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)