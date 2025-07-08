from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from agents.models import Agent
from agents.agent_processors import AgentProcessor
from wallet.stripe_handler import StripePaymentHandler
from wallet.models import WalletTransaction
import json


def homepage_view(request):
    """Homepage view showing all available agents"""
    agents = Agent.objects.filter(is_active=True)
    
    # Group agents by category
    categories = {}
    for agent in agents:
        category = agent.get_category_display()
        if category not in categories:
            categories[category] = []
        categories[category].append(agent)
    
    context = {
        'agents': agents,
        'categories': categories,
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
    }
    
    return render(request, 'core/homepage.html', context)


@login_required
def agent_detail_view(request, agent_slug):
    """Individual agent detail page"""
    agent = get_object_or_404(Agent, slug=agent_slug, is_active=True)
    
    # Check if user has sufficient balance
    can_use_agent = request.user.has_sufficient_balance(agent.price)
    
    # Get recent usage by this user
    recent_usage = WalletTransaction.objects.filter(
        user=request.user,
        agent_slug=agent_slug,
        type='agent_usage'
    )[:5]
    
    context = {
        'agent': agent,
        'can_use_agent': can_use_agent,
        'recent_usage': recent_usage,
        'user_balance': request.user.wallet_balance,
    }
    
    return render(request, 'core/agent_detail.html', context)


@login_required
@require_http_methods(["POST"])
def use_agent_view(request, agent_slug):
    """Process agent usage"""
    agent = get_object_or_404(Agent, slug=agent_slug, is_active=True)
    
    # Check balance
    if not request.user.has_sufficient_balance(agent.price):
        return JsonResponse({
            'success': False,
            'error': 'Insufficient balance'
        }, status=400)
    
    try:
        # Get input data based on agent type
        if agent_slug == 'data-analyzer':
            file_obj = request.FILES.get('file')
            if not file_obj:
                return JsonResponse({'success': False, 'error': 'File required'}, status=400)
            
            processor = AgentProcessor(agent_slug)
            result = processor.process_agent(file_obj=file_obj, user_id=request.user.id)
            
        elif agent_slug == 'five-whys':
            problem = request.POST.get('problem')
            if not problem:
                return JsonResponse({'success': False, 'error': 'Problem description required'}, status=400)
            
            processor = AgentProcessor(agent_slug)
            result = processor.process_agent(problem_description=problem, user_id=request.user.id)
            
        elif agent_slug == 'weather-reporter':
            location = request.POST.get('location')
            if not location:
                return JsonResponse({'success': False, 'error': 'Location required'}, status=400)
            
            processor = AgentProcessor(agent_slug)
            result = processor.process_agent(location=location)
            
        elif agent_slug == 'job-posting-generator':
            job_details = request.POST.get('job_details')
            if not job_details:
                return JsonResponse({'success': False, 'error': 'Job details required'}, status=400)
            
            processor = AgentProcessor(agent_slug)
            result = processor.process_agent(job_details=job_details, user_id=request.user.id)
            
        elif agent_slug == 'social-ads-generator':
            ad_requirements = request.POST.get('ad_requirements')
            if not ad_requirements:
                return JsonResponse({'success': False, 'error': 'Ad requirements required'}, status=400)
            
            processor = AgentProcessor(agent_slug)
            result = processor.process_agent(ad_requirements=ad_requirements, user_id=request.user.id)
            
        elif agent_slug == 'faq-generator':
            content_source = request.POST.get('content_source')
            if not content_source:
                return JsonResponse({'success': False, 'error': 'Content source required'}, status=400)
            
            processor = AgentProcessor(agent_slug)
            result = processor.process_agent(content_source=content_source, user_id=request.user.id)
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid agent'}, status=400)
        
        # Deduct balance and record transaction
        request.user.deduct_balance(
            amount=agent.price,
            description=f"Used {agent.name}",
            agent_slug=agent_slug
        )
        
        return JsonResponse({
            'success': True,
            'result': result,
            'remaining_balance': float(request.user.wallet_balance)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
                return redirect('wallet_topup')
            
            # Create Stripe checkout session
            stripe_handler = StripePaymentHandler()
            session_data = stripe_handler.create_checkout_session(request.user, amount)
            
            return redirect(session_data['payment_url'])
            
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount')
            return redirect('wallet_topup')
    
    return render(request, 'core/wallet_topup.html')


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
    agents = Agent.objects.filter(is_active=True)
    
    agents_data = []
    for agent in agents:
        agents_data.append({
            'id': agent.id,
            'name': agent.name,
            'slug': agent.slug,
            'description': agent.description,
            'category': agent.category,
            'price': float(agent.price),
            'icon': agent.icon,
            'rating': float(agent.rating),
            'review_count': agent.review_count,
        })
    
    return JsonResponse({
        'agents': agents_data,
        'total_count': len(agents_data)
    })
