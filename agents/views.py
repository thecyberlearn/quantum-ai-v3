from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Agent, AgentExecution, AgentCategory
from .serializers import AgentSerializer, AgentExecutionSerializer
import requests
import json
import time
import uuid

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_list(request):
    """List all active agents with optional category filtering"""
    agents = Agent.objects.filter(is_active=True)
    
    category = request.GET.get('category')
    if category:
        agents = agents.filter(category__slug=category)
    
    search = request.GET.get('search')
    if search:
        agents = agents.filter(name__icontains=search)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(agents, request)
    serializer = AgentSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_detail(request, slug):
    """Get detailed agent information"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    serializer = AgentSerializer(agent)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_agent(request):
    """Execute an agent with provided input data"""
    agent_slug = request.data.get('agent_slug')
    input_data = request.data.get('input_data', {})
    
    if not agent_slug:
        return Response({'error': 'agent_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    agent = get_object_or_404(Agent, slug=agent_slug, is_active=True)
    
    # Check if user has sufficient balance (using existing wallet system)
    if hasattr(request.user, 'has_sufficient_balance') and not request.user.has_sufficient_balance(agent.price):
        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create execution record
    execution = AgentExecution.objects.create(
        agent=agent,
        user=request.user,
        input_data=input_data,
        fee_charged=agent.price,
        status='pending'
    )
    
    try:
        # Deduct fee from user wallet (using existing wallet system)
        if hasattr(request.user, 'deduct_balance'):
            success = request.user.deduct_balance(
                agent.price, 
                f'{agent.name} - Execution {str(execution.id)[:8]}',
                agent.slug
            )
            if not success:
                execution.status = 'failed'
                execution.error_message = 'Failed to deduct wallet balance'
                execution.save()
                return Response({'error': 'Failed to deduct wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call n8n webhook with proper payload format
        execution.status = 'running'
        execution.save()
        
        # Generate session ID
        session_id = f"session_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        
        # Format message text for N8N based on agent type
        message_text = format_agent_message(agent.slug, input_data)
        
        webhook_payload = {
            'sessionId': session_id,
            'message': {'text': message_text},
            'webhookUrl': agent.webhook_url,
            'executionMode': 'production',
            'agentId': str(agent.id),
            'executionId': str(execution.id),
            'userId': str(request.user.id)
        }
        
        response = requests.post(
            agent.webhook_url,
            json=webhook_payload,
            timeout=90,  # Increased timeout for complex processing
            headers={'Content-Type': 'application/json'}
        )
        
        # Store webhook response
        execution.webhook_response = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'raw': response.text}
        
        if response.status_code == 200:
            execution.status = 'completed'
            execution.output_data = execution.webhook_response
        else:
            execution.status = 'failed'
            execution.error_message = f"Webhook returned {response.status_code}: {response.text[:500]}"
        
        execution.completed_at = timezone.now()
        execution.save()
        
        serializer = AgentExecutionSerializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except requests.RequestException as e:
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.completed_at = timezone.now()
        execution.save()
        
        return Response({
            'error': 'Failed to execute agent',
            'execution_id': str(execution.id)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_list(request):
    """List user's agent executions"""
    executions = AgentExecution.objects.filter(user=request.user)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(executions, request)
    serializer = AgentExecutionSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_detail(request, execution_id):
    """Get detailed execution information"""
    execution = get_object_or_404(AgentExecution, id=execution_id, user=request.user)
    serializer = AgentExecutionSerializer(execution)
    return Response(serializer.data)


def format_agent_message(agent_slug, input_data):
    """Format input data into a message for N8N webhook based on agent type"""
    if agent_slug == 'social-ads-generator':
        description = input_data.get('description', '')
        platform = input_data.get('social_platform', '')
        emoji = input_data.get('include_emoji', 'yes')
        language = input_data.get('language', 'English')
        
        return f"Execute Social Media Ad Creator with the following parameters:. Describe what you'd like to generate: {description}. Include Emoji: {emoji.title()}. For Social Media Platform: {platform.title()}. Language: {language}."
    
    # Default formatting for other agents
    params = [f"{key}: {value}" for key, value in input_data.items() if value]
    return f"Execute {agent_slug.replace('-', ' ').title()} with parameters: {'. '.join(params)}."


# Web interface views
def agent_detail_view(request, slug):
    """Render agent detail page with dynamic form"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    
    context = {
        'agent': agent,
        'timestamp': int(time.time())  # For cache busting
    }
    
    return render(request, 'agents/agent_detail.html', context)


def agents_marketplace(request):
    """Agent marketplace view"""
    agents = Agent.objects.filter(is_active=True).select_related('category')
    categories = AgentCategory.objects.filter(is_active=True)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        agents = agents.filter(category__slug=category_slug)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        agents = agents.filter(
            models.Q(name__icontains=search_query) |
            models.Q(short_description__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    context = {
        'agents': agents,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'timestamp': int(time.time())
    }
    
    return render(request, 'agents/marketplace.html', context)
