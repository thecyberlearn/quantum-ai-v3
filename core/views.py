from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from agent_base.models import BaseAgent
from wallet.stripe_handler import StripePaymentHandler
from wallet.models import WalletTransaction
import json
import datetime


def homepage_view(request):
    """Homepage view with agent system"""
    # Get featured agents for homepage
    featured_agents = BaseAgent.objects.filter(is_active=True).order_by('name')[:6]
    
    context = {
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
        'featured_agents': featured_agents,
    }
    
    return render(request, 'core/homepage.html', context)


def marketplace_view(request):
    """Professional marketplace view with agent system"""
    # Get all agents for marketplace
    agents = BaseAgent.objects.filter(is_active=True).order_by('category', 'name')
    
    # Filter by category if specified
    category = request.GET.get('category')
    if category:
        agents = agents.filter(category=category)
    
    # Get unique categories for filtering
    categories = BaseAgent.objects.filter(is_active=True).values_list('category', 'category').distinct()
    
    context = {
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
        'agents': agents,
        'categories': categories,
        'selected_category': category,
    }
    
    return render(request, 'core/marketplace.html', context)


def pricing_view(request):
    """Pricing page for non-logged-in users"""
    # If user is already logged in, redirect to wallet top-up
    if request.user.is_authenticated:
        return redirect('core:wallet_topup')
    
    # Get sample agents to show pricing context
    sample_agents = BaseAgent.objects.filter(is_active=True).order_by('name')[:4]
    
    context = {
        'sample_agents': sample_agents,
    }
    
    return render(request, 'core/pricing.html', context)


def agent_detail_view(request, agent_slug):
    """Agent detail view - redirect to specific agent app"""
    try:
        agent = BaseAgent.objects.get(slug=agent_slug, is_active=True)
        # Redirect to the specific agent app URL
        if agent_slug == 'weather-reporter':
            return redirect('/agents/weather-reporter/')
        else:
            # For other agents, redirect to marketplace for now
            messages.info(request, f'Agent "{agent.name}" page not yet available.')
            return redirect('core:marketplace')
    except BaseAgent.DoesNotExist:
        messages.error(request, 'Agent not found')
        return redirect('core:marketplace')




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
    
    return render(request, 'core/wallet.html', context)


@login_required
def wallet_topup_view(request):
    """Wallet top-up page"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        
        try:
            amount = float(amount)
            if amount not in [10, 50, 100, 500]:
                messages.error(request, 'Invalid amount selected')
                return redirect('core:wallet_topup')
            
            # Create Stripe checkout session
            stripe_handler = StripePaymentHandler()
            session_data = stripe_handler.create_checkout_session(request.user, amount, request)
            
            return redirect(session_data['payment_url'])
            
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount')
            return redirect('core:wallet_topup')
    
    return render(request, 'core/wallet_topup.html')


@login_required
def wallet_topup_success_view(request):
    """Payment success page with automatic payment verification (NO WEBHOOKS NEEDED)"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'No payment session found. Please contact support if you completed a payment.')
        return redirect('core:wallet')
    
    # Verify payment directly with Stripe API (bypasses webhook issues)
    try:
        from wallet.stripe_handler import StripePaymentHandler
        stripe_handler = StripePaymentHandler()
        
        print(f"💳 [SUCCESS PAGE] Verifying payment for session: {session_id}")
        result = stripe_handler.verify_payment(session_id)
        
        if result['success']:
            if result['processed']:
                messages.success(request, f'Payment successful! {result["amount"]} AED has been added to your wallet.')
                print(f"✅ [SUCCESS PAGE] Payment verified and wallet updated for user {request.user.id}")
            else:
                messages.info(request, 'Payment already processed. Your wallet balance is up to date.')
                print(f"ℹ️ [SUCCESS PAGE] Payment already processed for session {session_id}")
        else:
            messages.warning(request, f'Payment verification failed: {result.get("error", "Unknown error")}. Please contact support.')
            print(f"❌ [SUCCESS PAGE] Payment verification failed: {result}")
        
    except Exception as e:
        print(f"❌ [SUCCESS PAGE] Error verifying payment: {e}")
        messages.error(request, 'Unable to verify payment. Please contact support if you completed a payment.')
    
    return redirect('core:wallet')


@login_required
def wallet_topup_cancel_view(request):
    """Payment cancel page"""
    messages.info(request, 'Payment was cancelled. No charges were made.')
    return redirect('core:wallet_topup')




@login_required
def stripe_debug_view(request):
    """Debug endpoint to show Stripe API configuration and test connectivity"""
    import stripe
    from django.conf import settings
    
    debug_info = {
        'timestamp': datetime.datetime.now().isoformat(),
        'user_id': request.user.id,
        'user_email': request.user.email,
    }
    
    try:
        # Test Stripe API connectivity
        print(f"🔍 [STRIPE DEBUG] Testing Stripe API connectivity...")
        
        # Get API key info (masked)
        api_key = settings.STRIPE_SECRET_KEY
        debug_info['stripe_api_key_last4'] = api_key[-4:] if api_key else 'Not set'
        debug_info['stripe_api_key_prefix'] = api_key[:7] if api_key else 'Not set'
        debug_info['stripe_api_version'] = stripe.api_version
        
        # Test account connectivity
        try:
            account = stripe.Account.retrieve()
            debug_info['stripe_account'] = {
                'id': account.id,
                'email': account.email,
                'display_name': account.display_name,
                'country': account.country,
                'default_currency': account.default_currency,
                'business_profile': account.business_profile,
                'charges_enabled': account.charges_enabled,
                'payouts_enabled': account.payouts_enabled,
            }
            print(f"✅ [STRIPE DEBUG] Account connected: {account.id}")
        except Exception as account_error:
            debug_info['stripe_account_error'] = str(account_error)
            print(f"❌ [STRIPE DEBUG] Account error: {account_error}")
        
        # Test recent checkout sessions
        try:
            sessions = stripe.checkout.Session.list(limit=5)
            debug_info['recent_sessions'] = []
            for session in sessions.data:
                debug_info['recent_sessions'].append({
                    'id': session.id,
                    'status': session.status,
                    'payment_status': session.payment_status,
                    'amount_total': session.amount_total,
                    'currency': session.currency,
                    'customer_email': session.customer_email,
                    'client_reference_id': session.client_reference_id,
                    'created': session.created,
                    'metadata': session.metadata,
                })
            print(f"✅ [STRIPE DEBUG] Retrieved {len(sessions.data)} recent sessions")
        except Exception as sessions_error:
            debug_info['sessions_error'] = str(sessions_error)
            print(f"❌ [STRIPE DEBUG] Sessions error: {sessions_error}")
        
        # Test recent payments
        try:
            charges = stripe.Charge.list(limit=5)
            debug_info['recent_charges'] = []
            for charge in charges.data:
                debug_info['recent_charges'].append({
                    'id': charge.id,
                    'amount': charge.amount,
                    'currency': charge.currency,
                    'status': charge.status,
                    'paid': charge.paid,
                    'customer': charge.customer,
                    'description': charge.description,
                    'created': charge.created,
                    'metadata': charge.metadata,
                })
            print(f"✅ [STRIPE DEBUG] Retrieved {len(charges.data)} recent charges")
        except Exception as charges_error:
            debug_info['charges_error'] = str(charges_error)
            print(f"❌ [STRIPE DEBUG] Charges error: {charges_error}")
            
        debug_info['status'] = 'success'
        
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['status'] = 'error'
        print(f"❌ [STRIPE DEBUG] General error: {e}")
    
    return JsonResponse(debug_info, indent=2)




@csrf_exempt
def stripe_webhook_view(request):
    """Handle Stripe webhook events with comprehensive logging"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Log everything for debugging
    print(f"🎯 [{timestamp}] Stripe webhook received!")
    print(f"🎯 Method: {request.method}")
    print(f"🎯 Content-Type: {request.content_type}")
    print(f"🎯 Remote IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
    print(f"🎯 User Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}")
    print(f"🎯 Full headers: {dict(request.META)}")
    
    # Store in webhook logs for the test page
    webhook_log_entry = {
        'timestamp': timestamp,
        'method': request.method,
        'headers': dict(request.META),
        'body': request.body.decode('utf-8') if request.body else '',
        'content_type': request.content_type,
        'source': 'stripe_webhook',
        'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')
    }
    
    # Add to webhook logs
    webhook_logs.append(webhook_log_entry)
    if len(webhook_logs) > 50:
        webhook_logs.pop(0)
    
    if request.method != 'POST':
        print(f"❌ Invalid method: {request.method}")
        return JsonResponse({'status': 'error', 'message': f'Method {request.method} not allowed'}, status=405)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    print(f"📦 Payload length: {len(payload)} bytes")
    print(f"📦 Payload preview: {payload[:200]}...")
    print(f"🔐 Signature header: {sig_header is not None}")
    print(f"🔐 Full signature header: {sig_header}")
    
    # Always return success first to see if Stripe is reaching us
    if not sig_header:
        print(f"⚠️ No Stripe signature - might be a test request")
        return JsonResponse({'status': 'received', 'message': 'No signature verification'})
    
    stripe_handler = StripePaymentHandler()
    result = stripe_handler.handle_webhook(payload, sig_header)
    
    print(f"✅ Webhook result: {result}")
    
    if result['success']:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': result['error']}, status=400)


def agents_api_view(request):
    """API endpoint for agents list"""
    agents = BaseAgent.objects.filter(is_active=True)
    
    # Filter by category if specified
    category = request.GET.get('category')
    if category:
        agents = agents.filter(category=category)
    
    agents_data = []
    for agent in agents:
        agents_data.append({
            'id': str(agent.id),
            'name': agent.name,
            'slug': agent.slug,
            'description': agent.description,
            'category': agent.category,
            'price': float(agent.price),
            'icon': agent.icon,
            'rating': float(agent.rating),
            'review_count': agent.review_count,
            'agent_type': agent.agent_type,
        })
    
    return JsonResponse({
        'agents': agents_data,
        'total_count': len(agents_data),
    })