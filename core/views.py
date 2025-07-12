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
    """Payment success page"""
    messages.success(request, 'Payment successful! Your wallet balance has been updated.')
    return redirect('core:wallet')


@login_required
def wallet_topup_cancel_view(request):
    """Payment cancel page"""
    messages.info(request, 'Payment was cancelled. No charges were made.')
    return redirect('core:wallet_topup')


@login_required
def wallet_demo_view(request):
    """Demo page for testing Stripe webhook integration"""
    
    # Get recent transactions for debugging
    recent_transactions = request.user.wallet_transactions.all()[:10]
    
    # Get current balance
    current_balance = request.user.wallet_balance
    
    context = {
        'current_balance': current_balance,
        'recent_transactions': recent_transactions,
        'user_id': request.user.id,
        'user_email': request.user.email,
    }
    
    return render(request, 'core/wallet_demo.html', context)


@login_required
def wallet_demo_test_payment(request):
    """Test payment creation for webhook testing"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 10))
            
            # Validate amount
            if amount not in [10, 50, 100, 500]:
                return JsonResponse({'error': 'Invalid amount'}, status=400)
            
            print(f"🧪 DEMO: Creating test payment for {request.user.email}")
            print(f"🧪 DEMO: Amount: {amount} AED, User ID: {request.user.id}")
            
            # Create Stripe checkout session
            stripe_handler = StripePaymentHandler()
            session_data = stripe_handler.create_checkout_session(request.user, amount, request)
            
            return JsonResponse({
                'success': True,
                'payment_url': session_data['payment_url'],
                'session_id': session_data['session_id'],
                'user_id': request.user.id,
                'amount': amount
            })
            
        except Exception as e:
            print(f"🧪 DEMO: Error creating payment: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def wallet_demo_check_balance(request):
    """Check current wallet balance for demo"""
    request.user.refresh_from_db()
    
    # Get latest transactions
    recent_transactions = []
    for transaction in request.user.wallet_transactions.all()[:5]:
        recent_transactions.append({
            'amount': float(transaction.amount),
            'type': transaction.type,
            'description': transaction.description,
            'created_at': transaction.created_at.isoformat(),
            'stripe_session_id': transaction.stripe_session_id
        })
    
    return JsonResponse({
        'balance': float(request.user.wallet_balance),
        'user_id': request.user.id,
        'recent_transactions': recent_transactions,
        'timestamp': request.user.updated_at.isoformat() if hasattr(request.user, 'updated_at') else None
    })


# Simple webhook test page
def webhook_test_view(request):
    """Simple HTML page for webhook testing"""
    return render(request, 'core/webhook_test.html')


def stripe_webhook_test_view(request):
    """Stripe-specific webhook testing page"""
    return render(request, 'core/stripe_webhook_test.html')


# Store webhook logs in memory for the test page
webhook_logs = []

@csrf_exempt
def simple_webhook_test(request):
    """Ultra simple webhook endpoint for testing"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    log_entry = {
        'timestamp': timestamp,
        'method': request.method,
        'headers': dict(request.META),
        'body': request.body.decode('utf-8') if request.body else '',
        'content_type': request.content_type,
        'query_params': dict(request.GET),
    }
    
    # Store in memory (keep only last 50 logs)
    webhook_logs.append(log_entry)
    if len(webhook_logs) > 50:
        webhook_logs.pop(0)
    
    # Also print to console
    print(f"🧪 SIMPLE WEBHOOK [{timestamp}] Method: {request.method}")
    print(f"🧪 SIMPLE WEBHOOK [{timestamp}] Content-Type: {request.content_type}")
    print(f"🧪 SIMPLE WEBHOOK [{timestamp}] Body length: {len(request.body)} bytes")
    print(f"🧪 SIMPLE WEBHOOK [{timestamp}] Headers: {dict(request.META)}")
    
    # Return simple success response
    return HttpResponse("WEBHOOK RECEIVED OK", content_type="text/plain")


@csrf_exempt
def get_webhook_logs(request):
    """Get webhook logs for the test page"""
    try:
        return JsonResponse({'logs': webhook_logs})
    except Exception as e:
        print(f"Error in get_webhook_logs: {e}")
        return JsonResponse({'logs': [], 'error': str(e)})


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