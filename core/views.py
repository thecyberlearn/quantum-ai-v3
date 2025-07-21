from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from agent_base.models import BaseAgent
def homepage_view(request):
    """Homepage view with agent system"""
    # Get featured agents for homepage
    featured_agents = BaseAgent.objects.filter(is_active=True).order_by('name')[:6]
    
    context = {
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
        'featured_agents': featured_agents,
    }
    
    return render(request, 'core/homepage.html', context)
def pricing_view(request):
    """Pricing page for non-logged-in users"""
    # If user is already logged in, redirect to wallet top-up
    if request.user.is_authenticated:
        return redirect('wallet:wallet_topup')
    
    # Get sample agents to show pricing context
    sample_agents = BaseAgent.objects.filter(is_active=True).order_by('name')[:4]
    
    context = {
        'sample_agents': sample_agents,
    }
    
    return render(request, 'core/pricing.html', context)
