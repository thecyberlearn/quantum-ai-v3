"""
Direct access views for external form agents.
Handles payment processing and access to external forms (JotForm, Google Forms, etc.).
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from datetime import timedelta
from .models import AgentExecution
from .services import AgentFileService
from .utils import AgentCompat


def career_navigator_access(request):
    """Handle Try Now button click - charge wallet and redirect to form"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the Career Navigator.'
        return redirect('authentication:login')
    
    # Get the career navigator agent
    agent_data = AgentFileService.get_agent_by_slug('cybersec-career-navigator')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'Career Navigator is currently unavailable.')
        return redirect('agents:marketplace')
    
    agent_price = float(agent_data['price'])
    
    # Check if user has sufficient balance
    if not request.user.has_sufficient_balance(agent_price):
        messages.error(request, f'Insufficient balance! You need {agent_price} AED to access the Career Navigator.')
        return redirect('wallet:wallet')
    
    # Deduct fee from user wallet
    success = request.user.deduct_balance(
        agent_price, 
        f'{agent_data["name"]} - Direct Access',
        agent_data['slug']
    )
    
    if not success:
        messages.error(request, 'Failed to process payment. Please try again.')
        return redirect('agents:marketplace')
    
    # Create execution record for tracking
    execution = AgentExecution.objects.create(
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        input_data={'action': 'direct_access', 'source': 'try_now_button'},
        fee_charged=agent_price,
        status='completed',
        output_data={
            'type': 'direct_access',
            'message': f'Direct access granted to {agent_data["name"]}',
            'access_method': 'try_now_button'
        },
        completed_at=timezone.now()
    )
    
    # Redirect directly to form - no message needed
    return redirect('agents:career_navigator')


def career_navigator_view(request):
    """Display the career navigator form page"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the Career Navigator.'
        return redirect('authentication:login')
    
    # Get the career navigator agent
    agent_data = AgentFileService.get_agent_by_slug('cybersec-career-navigator')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'Career Navigator is currently unavailable.')
        return redirect('agents:marketplace')
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Check if user has a recent execution (within last 2 hours) or just redirect to payment
    recent_execution = AgentExecution.objects.filter(
        agent_slug=agent.slug,  # Changed to slug-based lookup
        user=request.user,
        status='completed',
        created_at__gte=timezone.now() - timedelta(hours=2)
    ).first()
    
    if not recent_execution:
        messages.info(request, 'Please click "Try Now" to access your Career Navigator consultation.')
        return redirect('agents:marketplace')
    
    context = {
        'agent': agent,
        'form_url': agent.webhook_url,
        'user_balance': request.user.wallet_balance,
        'execution': recent_execution
    }
    
    return render(request, 'career_navigator.html', context)


def ai_brand_strategist_view(request):
    """Display the AI Brand Strategist form page"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the AI Brand Strategist.'
        return redirect('authentication:login')
    
    # Get the AI Brand Strategist agent
    agent_data = AgentFileService.get_agent_by_slug('ai-brand-strategist')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'AI Brand Strategist is currently unavailable.')
        return redirect('agents:marketplace')
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Check if user has a recent execution (within last 2 hours) or just redirect to payment
    recent_execution = AgentExecution.objects.filter(
        agent_slug=agent.slug,  # Changed to slug-based lookup
        user=request.user,
        status='completed',
        created_at__gte=timezone.now() - timedelta(hours=2)
    ).first()
    
    if not recent_execution:
        messages.info(request, 'Please click "Try Now" to access your AI Brand Strategist consultation.')
        return redirect('agents:marketplace')
    
    context = {
        'agent': agent,
        'form_url': agent.webhook_url,
        'user_balance': request.user.wallet_balance,
        'execution': recent_execution
    }
    
    return render(request, 'ai_brand_strategist.html', context)


def ai_brand_strategist_access(request):
    """Handle Try Now button click - charge wallet and redirect to form"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the AI Brand Strategist.'
        return redirect('authentication:login')
    
    # Get the AI Brand Strategist agent
    agent_data = AgentFileService.get_agent_by_slug('ai-brand-strategist')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'AI Brand Strategist is currently unavailable.')
        return redirect('agents:marketplace')
    
    agent_price = float(agent_data['price'])
    
    # Check if user has sufficient balance
    if not request.user.has_sufficient_balance(agent_price):
        messages.error(request, f'Insufficient balance! You need {agent_price} AED to access the AI Brand Strategist.')
        return redirect('wallet:wallet')
    
    # Deduct fee from user wallet
    success = request.user.deduct_balance(
        agent_price, 
        f'{agent_data["name"]} - Direct Access',
        agent_data['slug']
    )
    
    if not success:
        messages.error(request, 'Failed to process payment. Please try again.')
        return redirect('agents:marketplace')
    
    # Create execution record for tracking
    execution = AgentExecution.objects.create(
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        input_data={'action': 'direct_access', 'source': 'try_now_button'},
        fee_charged=agent_price,
        status='completed',
        output_data={
            'type': 'direct_access',
            'message': f'Direct access granted to {agent_data["name"]}',
            'access_method': 'try_now_button'
        },
        completed_at=timezone.now()
    )
    
    # Redirect directly to form - no message needed
    return redirect('agents:ai_brand_strategist')


def lean_six_sigma_expert_view(request):
    """Display the Lean Six Sigma Expert form page"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the Lean Six Sigma Expert.'
        return redirect('authentication:login')
    
    # Get the Lean Six Sigma Expert agent
    agent_data = AgentFileService.get_agent_by_slug('lean-six-sigma-expert')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'Lean Six Sigma Expert is currently unavailable.')
        return redirect('agents:marketplace')
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Check if user has a recent execution (within last 2 hours) or just redirect to payment
    recent_execution = AgentExecution.objects.filter(
        agent_slug=agent.slug,  # Changed to slug-based lookup
        user=request.user,
        status='completed',
        created_at__gte=timezone.now() - timedelta(hours=2)
    ).first()
    
    if not recent_execution:
        messages.info(request, 'Please click "Try Now" to access your Lean Six Sigma Expert consultation.')
        return redirect('agents:marketplace')
    
    context = {
        'agent': agent,
        'form_url': agent.webhook_url,
        'user_balance': request.user.wallet_balance,
        'execution': recent_execution
    }
    
    return render(request, 'lean_six_sigma_expert.html', context)


def lean_six_sigma_expert_access(request):
    """Handle Try Now button click - charge wallet and redirect to form"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the Lean Six Sigma Expert.'
        return redirect('authentication:login')
    
    # Get the Lean Six Sigma Expert agent
    agent_data = AgentFileService.get_agent_by_slug('lean-six-sigma-expert')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'Lean Six Sigma Expert is currently unavailable.')
        return redirect('agents:marketplace')
    
    agent_price = float(agent_data['price'])
    
    # Check if user has sufficient balance
    if not request.user.has_sufficient_balance(agent_price):
        messages.error(request, f'Insufficient balance! You need {agent_price} AED to access the Lean Six Sigma Expert.')
        return redirect('wallet:wallet')
    
    # Deduct fee from user wallet
    success = request.user.deduct_balance(
        agent_price, 
        f'{agent_data["name"]} - Direct Access',
        agent_data['slug']
    )
    
    if not success:
        messages.error(request, 'Failed to process payment. Please try again.')
        return redirect('agents:marketplace')
    
    # Create execution record for tracking
    execution = AgentExecution.objects.create(
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        input_data={'action': 'direct_access', 'source': 'try_now_button'},
        fee_charged=agent_price,
        status='completed',
        output_data={
            'type': 'direct_access',
            'message': f'Direct access granted to {agent_data["name"]}',
            'access_method': 'try_now_button'
        },
        completed_at=timezone.now()
    )
    
    # Redirect directly to form - no message needed
    return redirect('agents:lean_six_sigma_expert')


def swot_analysis_expert_view(request):
    """Display the SWOT Analysis Expert form page"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the SWOT Analysis Expert.'
        return redirect('authentication:login')
    
    # Get the SWOT Analysis Expert agent
    agent_data = AgentFileService.get_agent_by_slug('swot-analysis-expert')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'SWOT Analysis Expert is currently unavailable.')
        return redirect('agents:marketplace')
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Check if user has a recent execution (within last 2 hours) or just redirect to payment
    recent_execution = AgentExecution.objects.filter(
        agent_slug=agent.slug,  # Changed to slug-based lookup
        user=request.user,
        status='completed',
        created_at__gte=timezone.now() - timedelta(hours=2)
    ).first()
    
    if not recent_execution:
        messages.info(request, 'Please click "Try Now" to access your SWOT Analysis Expert consultation.')
        return redirect('agents:marketplace')
    
    context = {
        'agent': agent,
        'form_url': agent.webhook_url,
        'user_balance': request.user.wallet_balance,
        'execution': recent_execution
    }
    
    return render(request, 'swot_analysis_expert.html', context)


def swot_analysis_expert_access(request):
    """Handle Try Now button click - charge wallet and redirect to form"""
    if not request.user.is_authenticated:
        # Clear all existing messages before adding login message
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Consume all messages
        # Add login message to session for after login redirect
        request.session['post_login_message'] = 'Please complete your login to access the SWOT Analysis Expert.'
        return redirect('authentication:login')
    
    # Get the SWOT Analysis Expert agent
    agent_data = AgentFileService.get_agent_by_slug('swot-analysis-expert')
    if not agent_data or not agent_data.get('is_active', True):
        messages.error(request, 'SWOT Analysis Expert is currently unavailable.')
        return redirect('agents:marketplace')
    
    agent_price = float(agent_data['price'])
    
    # Check if user has sufficient balance
    if not request.user.has_sufficient_balance(agent_price):
        messages.error(request, f'Insufficient balance! You need {agent_price} AED to access the SWOT Analysis Expert.')
        return redirect('wallet:wallet')
    
    # Deduct fee from user wallet
    success = request.user.deduct_balance(
        agent_price, 
        f'{agent_data["name"]} - Direct Access',
        agent_data['slug']
    )
    
    if not success:
        messages.error(request, 'Failed to process payment. Please try again.')
        return redirect('agents:marketplace')
    
    # Create execution record for tracking
    execution = AgentExecution.objects.create(
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        input_data={'action': 'direct_access', 'source': 'try_now_button'},
        fee_charged=agent_price,
        status='completed',
        output_data={
            'type': 'direct_access',
            'message': f'Direct access granted to {agent_data["name"]}',
            'access_method': 'try_now_button'
        },
        completed_at=timezone.now()
    )
    
    # Redirect directly to form - no message needed
    return redirect('agents:swot_analysis_expert')


@login_required
def direct_access_handler(request, slug):
    """
    Generic handler for direct access agents (external forms like JotForm).
    Handles payment processing and grants access to external form.
    """
    agent_data = AgentFileService.get_agent_by_slug(slug)
    if not agent_data or not agent_data.get('is_active', True):
        raise Http404("Agent not found")
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Verify this is a direct access agent
    if not agent.access_url_name or not agent.display_url_name:
        messages.error(request, 'This agent does not support direct access.')
        return redirect('agents:marketplace')
    
    agent_price = agent.price
    
    # Handle payment for paid agents
    if agent_price > 0:
        user_balance = request.user.wallet_balance
        if user_balance < agent_price:
            messages.error(request, f'Insufficient balance. You need {agent_price} AED but have {user_balance} AED.')
            return redirect('wallet:wallet')
        
        # Process payment
        try:
            from wallet.models import WalletTransaction
            WalletTransaction.objects.create(
                user=request.user,
                amount=-agent_price,
                type='agent_usage',
                description=f'Payment for {agent.name}',
                agent_slug=agent.slug
            )
        except Exception as e:
            messages.error(request, 'Payment processing failed. Please try again.')
            return redirect('agents:agent_detail', slug=slug)
    
    # Grant access - redirect directly to display page
    return redirect('agents:direct_access_display', slug=slug)


@login_required  
def direct_access_display(request, slug):
    """
    Generic display handler for direct access agents.
    Shows external form (JotForm, Google Forms, etc.) in iframe or redirects directly.
    """
    agent_data = AgentFileService.get_agent_by_slug(slug)
    if not agent_data or not agent_data.get('is_active', True):
        raise Http404("Agent not found")
    
    # Convert to compatible object
    agent = AgentCompat(agent_data)
    
    # Verify this is a direct access agent
    if not agent.access_url_name or not agent.display_url_name:
        messages.error(request, 'This agent does not support direct access.')
        return redirect('agents:marketplace')
    
    # For now, redirect directly to external form
    # Future: Can render iframe template or custom display logic
    return redirect(agent.webhook_url)