from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import {{ agent_name_camel }}Request, {{ agent_name_camel }}Response
from .processor import {{ agent_name_camel }}Processor
import json


@login_required
def {{ agent_slug_underscore }}_detail(request):
    """Detail page for {{ agent_name }} agent"""
    try:
        agent = BaseAgent.objects.get(slug='{{ agent_slug }}')
    except BaseAgent.DoesNotExist:
        messages.error(request, '{{ agent_name }} agent not found.')
        return redirect('core:homepage')
    
    # Get user's recent requests
    user_requests = {{ agent_name_camel }}Request.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'agent': agent,
        'user_requests': user_requests
    }
    return render(request, '{{ agent_slug_underscore }}/detail.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class {{ agent_name_camel }}ProcessView(View):
    """Process {{ agent_name }} requests"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Parse request data
            {% if agent_type == 'api' and 'pdf' in agent_slug %}# Handle multipart form data for file uploads
            data = request.POST.dict()
            files = request.FILES
            {% else %}data = json.loads(request.body){% endif %}
            
            # Get agent
            agent = BaseAgent.objects.get(slug='{{ agent_slug }}')
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Create request object (no wallet deduction yet - only after successful processing)
            agent_request = {{ agent_name_camel }}Request.objects.create(
                user=request.user,
                agent=agent,
                cost=agent.price,
                {% for field in request_creation %}{{ field.name }}=data.get('{{ field.source }}', '{{ field.default }}'),
                {% endfor %}
            )
            
            # Process request
            processor = {{ agent_name_camel }}Processor()
            result = processor.process_request(
                request_obj=agent_request,
                user_id=request.user.id,
                {% for param in processor_params %}{{ param.name }}=data.get('{{ param.source }}'),
                {% endfor %}
            )
            
            # Refresh user from database to get updated wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'request_id': str(agent_request.id),
                'message': '{{ agent_name }} request processed successfully',
                'wallet_balance': float(request.user.wallet_balance)
            })
            
        except BaseAgent.DoesNotExist:
            return JsonResponse({'error': '{{ agent_name }} agent not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def {{ agent_slug_underscore }}_result(request, request_id):
    """Get result for a specific request"""
    try:
        agent_request = {{ agent_name_camel }}Request.objects.get(
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
                {% for field in result_fields %}'{{ field.name }}': getattr(response, '{{ field.name }}', None),
                {% endfor %}'processing_time': float(response.processing_time) if response.processing_time else None,
                'error_message': response.error_message,
                'wallet_balance': float(request.user.wallet_balance)
            })
        else:
            return JsonResponse({
                'success': False,
                'status': agent_request.status,
                'message': 'Processing in progress...'
            })
            
    except {{ agent_name_camel }}Request.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)