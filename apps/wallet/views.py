from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from .stripe_handler import StripeHandler
import json
import stripe

User = get_user_model()

@login_required
@require_http_methods(["POST"])
def create_checkout_session(request):
    """Create Stripe checkout session for wallet top-up"""
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        package_id = data.get('package_id')
        
        if not amount or amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Create Stripe checkout session
        stripe_handler = StripeHandler()
        session = stripe_handler.create_checkout_session(
            amount=amount,
            user_id=request.user.id,
            package_id=package_id
        )
        
        return JsonResponse({'checkout_url': session.url})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        stripe_handler = StripeHandler()
        stripe_handler.handle_webhook_event(event)
        
        return HttpResponse(status=200)
        
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(status=500)

@login_required
def payment_success(request):
    """Handle successful payment redirect"""
    session_id = request.GET.get('session_id')
    if session_id:
        messages.success(request, '✅ Payment successful! Your wallet has been topped up.')
    return redirect('pricing')

@login_required
def payment_cancel(request):
    """Handle cancelled payment redirect"""
    messages.error(request, '❌ Payment was cancelled. No charges were made.')
    return redirect('pricing')
