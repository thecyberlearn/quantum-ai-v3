"""
REST API views for agent execution and management.
Handles API endpoints for executing agents, retrieving execution history, etc.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import AgentExecution
from .serializers import AgentExecutionSerializer
from .services import AgentFileService
from .utils import validate_webhook_url, format_agent_message
import requests
import time
import uuid


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_agent(request):
    """Execute an agent with provided input data"""
    agent_slug = request.data.get('agent_slug')
    input_data = request.data.get('input_data', {})
    
    if not agent_slug:
        return Response({'error': 'agent_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    agent_data = AgentFileService.get_agent_by_slug(agent_slug)
    if not agent_data or not agent_data.get('is_active', True):
        return Response({'error': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)
    
    agent_price = float(agent_data['price'])
    
    # Check if user has sufficient balance (using existing wallet system)
    if hasattr(request.user, 'has_sufficient_balance') and not request.user.has_sufficient_balance(agent_price):
        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create execution record
    execution = AgentExecution.objects.create(
        agent_slug=agent_data['slug'],
        agent_name=agent_data['name'],
        user=request.user,
        input_data=input_data,
        fee_charged=agent_price,
        status='pending'
    )
    
    try:
        # Deduct fee from user wallet (using existing wallet system)
        if hasattr(request.user, 'deduct_balance'):
            success = request.user.deduct_balance(
                agent_price, 
                f'{agent_data["name"]} - Execution {str(execution.id)[:8]}',
                agent_data['slug']
            )
            if not success:
                execution.status = 'failed'
                execution.error_message = 'Failed to deduct wallet balance'
                execution.save()
                return Response({'error': 'Failed to deduct wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate webhook URL to prevent SSRF attacks
        try:
            validate_webhook_url(agent_data['webhook_url'])
        except ValueError as e:
            execution.status = 'failed'
            execution.error_message = f'Invalid webhook URL: {str(e)}'
            execution.save()
            return Response({'error': f'Invalid webhook URL: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call n8n webhook with proper payload format
        execution.status = 'running'
        execution.save()
        
        # Generate session ID
        session_id = f"session_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        
        # Format message text for N8N based on agent type
        message_text = format_agent_message(agent_data['slug'], input_data)
        
        webhook_payload = {
            'sessionId': session_id,
            'message': {'text': message_text},
            'webhookUrl': agent_data['webhook_url'],
            'executionMode': 'production',
            'agentId': agent_data['slug'],
            'executionId': str(execution.id),
            'userId': str(request.user.id)
        }
        
        response = requests.post(
            agent_data['webhook_url'],
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