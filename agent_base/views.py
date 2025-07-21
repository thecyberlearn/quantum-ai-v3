from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import BaseAgent


def marketplace_view(request):
    """Professional marketplace view with agent system"""
    # Get all agents for marketplace with optimized query
    agents_queryset = BaseAgent.objects.filter(is_active=True).select_related().order_by('category', 'name')
    
    # Filter by category if specified
    category = request.GET.get('category')
    if category:
        agents_queryset = agents_queryset.filter(category=category)
    
    # Get agents and categories in single query
    agents = list(agents_queryset)
    categories = BaseAgent.objects.filter(is_active=True).values_list('category', 'category').distinct()
    
    context = {
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
        'agents': agents,
        'categories': categories,
        'selected_category': category,
    }
    
    return render(request, 'agent_base/marketplace.html', context)


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
            return redirect('agent_base:marketplace')
    except BaseAgent.DoesNotExist:
        messages.error(request, 'Agent not found')
        return redirect('agent_base:marketplace')


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