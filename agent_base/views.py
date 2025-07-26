from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
from .models import BaseAgent
import logging

logger = logging.getLogger('agent_base.security')


@ratelimit(key='ip', rate='60/m', method='GET', block=False)
def marketplace_view(request):
    """Professional marketplace view with agent system - Rate limited to 60 requests per minute per IP"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Marketplace rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many requests. Please wait a moment before refreshing.')
        # Still show marketplace but with warning
    
    # Get all agents for marketplace with optimized query
    agents_queryset = BaseAgent.objects.filter(is_active=True).select_related().order_by('category', 'name')
    
    # Server-side search with validation
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Validate search query (max length and safe characters)
        if len(search_query) > 100:
            logger.warning(f"Search query too long: {len(search_query)} characters")
            messages.error(request, 'Search query too long. Please keep it under 100 characters.')
            search_query = search_query[:100]
        
        # Remove potential SQL injection patterns and sanitize
        import re
        search_query = re.sub(r'[^\w\s\-\.]', '', search_query)
        
        if search_query:
            agents_queryset = agents_queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            logger.info(f"Marketplace search performed: '{search_query}'")
    
    # Filter by category if specified with validation
    category = request.GET.get('category')
    if category:
        # Validate category against allowed choices
        valid_categories = [choice[0] for choice in BaseAgent.CATEGORIES]
        if category in valid_categories:
            agents_queryset = agents_queryset.filter(category=category)
            logger.info(f"Marketplace filtered by valid category: {category}")
        else:
            logger.warning(f"Invalid category parameter attempted: {category}")
            category = None  # Reset to show all agents
    
    # Get agents and categories in single query
    agents = list(agents_queryset)
    categories = BaseAgent.objects.filter(is_active=True).values_list('category', 'category').distinct()
    
    context = {
        'user_balance': request.user.wallet_balance if request.user.is_authenticated else 0,
        'agents': agents,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query if 'search_query' in locals() else '',
    }
    
    return render(request, 'agent_base/marketplace.html', context)



@ratelimit(key='ip', rate='30/m', method='GET', block=False)
def agents_api_view(request):
    """API endpoint for agents list - Rate limited to 30 requests per minute per IP"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Agents API rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({
            'error': 'Rate limit exceeded. Please try again later.',
            'agents': [],
            'total_count': 0,
        }, status=429)
    
    agents = BaseAgent.objects.filter(is_active=True)
    
    # Server-side search with validation for API
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Validate search query (max length and safe characters)
        if len(search_query) > 100:
            logger.warning(f"API search query too long: {len(search_query)} characters")
            return JsonResponse({
                'error': 'Search query too long. Maximum 100 characters allowed.',
                'agents': [],
                'total_count': 0,
            }, status=400)
        
        # Remove potential SQL injection patterns and sanitize
        import re
        search_query = re.sub(r'[^\w\s\-\.]', '', search_query)
        
        if search_query:
            agents = agents.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            logger.info(f"API search performed: '{search_query}'")
    
    # Filter by category if specified with validation
    category = request.GET.get('category')
    if category:
        # Validate category against allowed choices
        valid_categories = [choice[0] for choice in BaseAgent.CATEGORIES]
        if category in valid_categories:
            agents = agents.filter(category=category)
            logger.info(f"API filtered by valid category: {category}")
        else:
            logger.warning(f"Invalid category parameter in API: {category}")
            return JsonResponse({
                'error': 'Invalid category parameter',
                'valid_categories': valid_categories,
                'agents': [],
                'total_count': 0,
            }, status=400)
    
    # Add pagination for security (limit large responses) with validation
    try:
        page_size = min(int(request.GET.get('limit', 50)), 100)  # Max 100 agents per request
        offset = max(int(request.GET.get('offset', 0)), 0)
    except (ValueError, TypeError):
        logger.warning(f"Invalid pagination parameters in API request")
        return JsonResponse({
            'error': 'Invalid pagination parameters. Limit and offset must be integers.',
            'agents': [],
            'total_count': 0,
        }, status=400)
    
    agents_page = agents[offset:offset + page_size]
    
    # Only return essential data (minimize information disclosure)
    agents_data = []
    for agent in agents_page:
        agents_data.append({
            'name': agent.name,
            'slug': agent.slug,
            'description': agent.description[:200],  # Limit description length
            'category': agent.category,
            'price': float(agent.price),
            'icon': agent.icon,
            'rating': float(agent.rating),
        })
    
    return JsonResponse({
        'agents': agents_data,
        'total_count': agents.count(),
        'returned_count': len(agents_data),
        'offset': offset,
        'limit': page_size,
    })