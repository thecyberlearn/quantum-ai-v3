from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import WeatherReporterRequest, WeatherReporterResponse
from .processor import WeatherReporterProcessor
import json


@login_required
def weather_reporter_detail(request):
    """Detail page for Weather Reporter agent"""
    try:
        agent = BaseAgent.objects.get(slug='weather-reporter')
    except BaseAgent.DoesNotExist:
        messages.error(request, 'Weather Reporter agent not found.')
        return redirect('core:homepage')
    
    # Get user requests only if authenticated
    user_requests = []
    if request.user.is_authenticated:
        user_requests = WeatherReporterRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'agent': agent,
        'user_requests': user_requests
    }
    return render(request, 'weather_reporter/detail.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class WeatherReporterProcessView(View):
    """Process Weather Reporter requests"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Handle FormData from frontend
            data = request.POST.dict()
            
            # Get agent
            agent = BaseAgent.objects.get(slug='weather-reporter')
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Create request object (no wallet deduction yet - only after successful processing)
            agent_request = WeatherReporterRequest.objects.create(
                user=request.user,
                agent=agent,
                cost=agent.price,
                location=data.get('location', ''),
                report_type=data.get('report_type', 'current'),
                
            )
            
            # Process request immediately (API-based agent)
            processor = WeatherReporterProcessor()
            result = processor.process_request(
                request_obj=agent_request,
                user_id=request.user.id,
                location=data.get('location'),
                report_type=data.get('report_type'),
            )
            
            # Refresh user from database to get updated wallet balance
            request.user.refresh_from_db()
            
            # Check if we have a response object
            if hasattr(agent_request, 'response'):
                response_obj = agent_request.response
                return JsonResponse({
                    'success': response_obj.success,
                    'status': 'completed',
                    'content': response_obj.formatted_report,
                    'weather_data': response_obj.weather_data,
                    'temperature': response_obj.temperature,
                    'description': response_obj.description,
                    'humidity': response_obj.humidity,
                    'wind_speed': response_obj.wind_speed,
                    'formatted_report': response_obj.formatted_report,
                    'processing_time': float(response_obj.processing_time) if response_obj.processing_time else None,
                    'wallet_balance': float(request.user.wallet_balance)
                })
            else:
                # Fallback if no response object
                return JsonResponse({
                    'success': True,
                    'status': 'completed',
                    'message': 'Weather report generated successfully',
                    'wallet_balance': float(request.user.wallet_balance)
                })
            
        except BaseAgent.DoesNotExist:
            return JsonResponse({'error': 'Weather Reporter agent not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def weather_reporter_result(request, request_id):
    """Get result for a specific request"""
    try:
        agent_request = WeatherReporterRequest.objects.get(
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
                'weather_data': getattr(response, 'weather_data', None),
                'temperature': getattr(response, 'temperature', None),
                'description': getattr(response, 'description', None),
                'humidity': getattr(response, 'humidity', None),
                'wind_speed': getattr(response, 'wind_speed', None),
                'formatted_report': getattr(response, 'formatted_report', None),
                
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
            
    except WeatherReporterRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)