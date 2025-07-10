from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import JobPostingGeneratorRequest, JobPostingGeneratorResponse
from .processor import JobPostingGeneratorProcessor
import json


def job_posting_generator_detail(request):
    """Detail page for Job Posting Generator agent"""
    try:
        agent = BaseAgent.objects.get(slug='job-posting-generator')
    except BaseAgent.DoesNotExist:
        messages.error(request, 'Job Posting Generator agent not found.')
        return redirect('core:homepage')
    
    if request.method == 'POST':
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            try:
                # Create request object (no wallet deduction yet)
                agent_request = JobPostingGeneratorRequest.objects.create(
                    user=request.user,
                    agent=agent,
                    cost=agent.price,
                    job_title=request.POST.get('job_title'),
                    company_name=request.POST.get('company_name'),
                    job_description=request.POST.get('job_description'),
                    seniority_level=request.POST.get('seniority_level'),
                    contract_type=request.POST.get('contract_type'),
                    location=request.POST.get('location'),
                    language=request.POST.get('language', 'English'),
                    company_website=request.POST.get('company_website', ''),
                    how_to_apply=request.POST.get('how_to_apply', ''),
                )
                
                # Process request
                processor = JobPostingGeneratorProcessor()
                result = processor.process_request(
                    request_obj=agent_request,
                    user_id=request.user.id,
                )
                
                # Refresh user from database to get updated wallet balance
                request.user.refresh_from_db()
                
                return JsonResponse({
                    'success': True,
                    'request_id': str(agent_request.id),
                    'message': 'Job posting generation started',
                    'wallet_balance': float(request.user.wallet_balance)
                })
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        # Regular form submission (redirect to avoid resubmission)
        return redirect('job_posting_generator:detail')
    
    # GET request - show form
    context = {
        'agent': agent,
    }
    return render(request, 'job_posting_generator/detail.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class JobPostingGeneratorProcessView(View):
    """Process Job Posting Generator requests"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Get agent
            agent = BaseAgent.objects.get(slug='job-posting-generator')
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Create request object (no wallet deduction yet - only after successful processing)
            agent_request = JobPostingGeneratorRequest.objects.create(
                user=request.user,
                agent=agent,
                cost=agent.price,
                job_title=data.get('job_title'),
                company_name=data.get('company_name'),
                job_description=data.get('job_description'),
                seniority_level=data.get('seniority_level'),
                contract_type=data.get('contract_type'),
                location=data.get('location'),
                language=data.get('language', 'English'),
                company_website=data.get('company_website', ''),
                how_to_apply=data.get('how_to_apply', ''),
            )
            
            # Process request
            processor = JobPostingGeneratorProcessor()
            result = processor.process_request(
                request_obj=agent_request,
                user_id=request.user.id,
            )
            
            # Refresh user from database to get updated wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'request_id': str(agent_request.id),
                'message': 'Job Posting Generator request processed successfully',
                'wallet_balance': float(request.user.wallet_balance)
            })
            
        except BaseAgent.DoesNotExist:
            return JsonResponse({'error': 'Job Posting Generator agent not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def job_posting_generator_result(request, request_id):
    """Get result for a specific request"""
    try:
        agent_request = JobPostingGeneratorRequest.objects.get(
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
                'content': getattr(response, 'job_posting_content', None),
                'job_posting_content': getattr(response, 'job_posting_content', None),
                'formatted_posting': getattr(response, 'formatted_posting', None),
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
            
    except JobPostingGeneratorRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)