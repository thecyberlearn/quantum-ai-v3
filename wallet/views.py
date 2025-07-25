from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
from .stripe_handler import StripePaymentHandler
import datetime
import stripe
from django.conf import settings
import logging
import ipaddress

logger = logging.getLogger(__name__)

# Stripe webhook IP ranges for security validation
STRIPE_WEBHOOK_IPS = [
    '3.18.12.0/24', '3.130.192.0/24', '13.235.14.0/24', '13.235.122.0/24',
    '18.211.135.0/24', '35.154.171.0/24', '52.15.183.0/24', '54.187.174.0/24',
    '54.187.205.0/24', '54.187.216.0/24', '54.241.31.0/24', '54.241.31.99/32',
    '54.241.31.102/32'
]


@login_required
def wallet_view(request):
    """Wallet management page"""
    transactions = request.user.wallet_transactions.all()[:50]
    
    # Calculate statistics
    total_spent = sum(abs(t.amount) for t in transactions if t.type == 'agent_usage')
    total_topped_up = sum(t.amount for t in transactions if t.type == 'top_up')
    
    context = {
        'transactions': transactions,
        'total_spent': total_spent,
        'total_topped_up': total_topped_up,
        'current_balance': request.user.wallet_balance,
    }
    
    return render(request, 'wallet/wallet.html', context)


@login_required
@ratelimit(key='user', rate='5/m', method=UNSAFE, block=False)
def wallet_topup_view(request):
    """Wallet top-up page with rate limiting (5 attempts per minute per user)"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Wallet top-up rate limit exceeded for user {request.user.id}")
        messages.error(request, 'Too many top-up attempts. Please try again in a few minutes.')
        return render(request, 'wallet/wallet_topup.html')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        
        try:
            amount = float(amount)
            if amount not in [10, 50, 100, 500]:
                logger.warning(f"Invalid amount attempted by user {request.user.id}: {amount}")
                messages.error(request, 'Invalid amount selected')
                return redirect('wallet:wallet_topup')
            
            # Create Stripe checkout session
            stripe_handler = StripePaymentHandler()
            session_data = stripe_handler.create_checkout_session(request.user, amount, request)
            
            logger.info(f"Checkout session created for user {request.user.id}, amount: {amount} AED")
            return redirect(session_data['payment_url'])
            
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid amount format from user {request.user.id}: {e}")
            messages.error(request, 'Invalid amount')
            return redirect('wallet:wallet_topup')
        except Exception as e:
            logger.error(f"Checkout session creation failed for user {request.user.id}: {e}")
            messages.error(request, 'Unable to process payment at this time. Please try again.')
            return redirect('wallet:wallet_topup')
    
    return render(request, 'wallet/wallet_topup.html')


@login_required
@ratelimit(key='user', rate='10/m', method='GET', block=False)
def wallet_topup_success_view(request):
    """Payment success page with automatic payment verification"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Payment success page rate limit exceeded for user {request.user.id}")
        messages.error(request, 'Too many verification attempts. Please wait a moment.')
        return redirect('wallet:wallet')
    
    session_id = request.GET.get('session_id')
    
    if not session_id:
        logger.warning(f"No session ID provided for user {request.user.id}")
        messages.error(request, 'No payment session found. Please contact support if you completed a payment.')
        return redirect('wallet:wallet')
    
    # Verify payment directly with Stripe API
    try:
        stripe_handler = StripePaymentHandler()
        
        logger.info(f"Verifying payment for user {request.user.id}, session: {session_id}")
        result = stripe_handler.verify_payment(session_id)
        
        if result['success']:
            if result['processed']:
                messages.success(request, f'Payment successful! {result["amount"]} AED has been added to your wallet.')
                logger.info(f"Payment verified and wallet updated for user {request.user.id}")
            else:
                messages.info(request, 'Payment already processed. Your wallet balance is up to date.')
                logger.info(f"Payment already processed for session {session_id}")
        else:
            messages.warning(request, 'Payment verification failed. Please contact support.')
            logger.error(f"Payment verification failed for user {request.user.id}: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Error verifying payment for user {request.user.id}: {e}")
        messages.error(request, 'Unable to verify payment. Please contact support if you completed a payment.')
    
    return redirect('wallet:wallet')


@login_required
def wallet_topup_cancel_view(request):
    """Payment cancel page"""
    messages.info(request, 'Payment was cancelled. No charges were made.')
    return redirect('wallet:wallet_topup')


@login_required
@user_passes_test(lambda u: u.is_superuser)
@ratelimit(key='user', rate='3/m', method='GET', block=True)
def stripe_debug_view(request):
    """Secure debug endpoint for superusers only"""
    if not request.user.is_superuser:
        logger.warning(f"Unauthorized debug access attempt by user {request.user.id}")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    
    debug_info = {
        'timestamp': datetime.datetime.now().isoformat(),
        'user_id': request.user.id,
        'environment': 'production' if not settings.DEBUG else 'development',
    }
    
    try:
        # Basic connectivity test without exposing sensitive data
        api_key = settings.STRIPE_SECRET_KEY
        debug_info['stripe_api_configured'] = bool(api_key)
        debug_info['stripe_api_version'] = stripe.api_version
        
        # Test account connectivity (minimal info)
        try:
            account = stripe.Account.retrieve()
            debug_info['stripe_account'] = {
                'id': account.id[:8] + '...',  # Partial ID only
                'charges_enabled': account.charges_enabled,
                'payouts_enabled': account.payouts_enabled,
            }
            logger.info(f"Stripe debug accessed by superuser {request.user.id}")
        except Exception as account_error:
            debug_info['stripe_account_error'] = 'Connection failed'
            logger.error(f"Stripe account error in debug: {account_error}")
        
        debug_info['status'] = 'success'
        
    except Exception as e:
        debug_info['error'] = 'Configuration error'
        debug_info['status'] = 'error'
        logger.error(f"Stripe debug error: {e}")
    
    return JsonResponse(debug_info, indent=2)


def is_stripe_ip(ip_address):
    """Check if IP address is from Stripe's webhook IP ranges"""
    try:
        ip = ipaddress.ip_address(ip_address)
        for ip_range in STRIPE_WEBHOOK_IPS:
            if ip in ipaddress.ip_network(ip_range):
                return True
    except ValueError:
        return False
    return False

@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='50/m', method='POST', block=True)
def stripe_webhook_view(request):
    """Secure Stripe webhook handler with IP validation and rate limiting"""
    timestamp = datetime.datetime.now().isoformat()
    remote_ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    # Security: Validate request comes from Stripe
    if not is_stripe_ip(remote_ip) and not settings.DEBUG:
        logger.warning(f"Webhook from unauthorized IP: {remote_ip}")
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
    
    # Security: Validate content type
    if request.content_type != 'application/json':
        logger.warning(f"Invalid content type from {remote_ip}: {request.content_type}")
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)
    
    # Security: Validate payload size (max 64KB)
    if len(request.body) > 65536:
        logger.warning(f"Oversized payload from {remote_ip}: {len(request.body)} bytes")
        return JsonResponse({'status': 'error', 'message': 'Payload too large'}, status=413)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    logger.info(f"Webhook received from {remote_ip}, payload size: {len(payload)} bytes")
    
    if not sig_header:
        logger.warning(f"No Stripe signature from {remote_ip}")
        return JsonResponse({'status': 'error', 'message': 'No signature'}, status=400)
    
    try:
        stripe_handler = StripePaymentHandler()
        result = stripe_handler.handle_webhook(payload, sig_header)
        
        if result['success']:
            logger.info(f"Webhook processed successfully from {remote_ip}")
            return JsonResponse({'status': 'success'})
        else:
            logger.error(f"Webhook processing failed from {remote_ip}: {result['error']}")
            return JsonResponse({'status': 'error', 'message': 'Processing failed'}, status=400)
            
    except Exception as e:
        logger.error(f"Webhook error from {remote_ip}: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal error'}, status=500)