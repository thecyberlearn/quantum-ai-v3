from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
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


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook_view(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    stripe_handler = StripePaymentHandler()
    result = stripe_handler.handle_webhook(payload, sig_header)
    
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
