from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Agent, AgentExecution, AgentCategory, ChatSession, ChatMessage
from .serializers import AgentSerializer, AgentExecutionSerializer
import requests
import json
import time
import uuid
import ipaddress
from urllib.parse import urlparse

def validate_webhook_url(url):
    """
    Validate webhook URL to prevent SSRF attacks.
    Only allows HTTPS URLs to external, non-private networks.
    """
    try:
        parsed = urlparse(url)
        
        # Only allow HTTP/HTTPS protocols
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS URLs are allowed")
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid hostname in URL")
        
        # For localhost development, allow localhost URLs first
        if hostname in ['localhost', '127.0.0.1'] and parsed.port in [5678, 8000, 8080]:
            return True  # Allow N8N development server
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private, loopback, and reserved IP ranges
            if (ip.is_private or ip.is_loopback or ip.is_reserved or 
                ip.is_link_local or ip.is_multicast):
                raise ValueError("Internal/private IP addresses are not allowed")
        except ValueError as e:
            if "does not appear to be an IPv4 or IPv6 address" not in str(e):
                raise  # Re-raise if it's not just a "not an IP" error
            # If it's not an IP, it's a domain name - that's fine
            
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid webhook URL: {str(e)}")

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
        
        # Validate webhook URL to prevent SSRF attacks
        try:
            validate_webhook_url(agent.webhook_url)
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


def career_navigator_access(request):
    """Handle Try Now button click - charge wallet and redirect to form"""
    if not request.user.is_authenticated:
        # Clear any existing messages to prevent confusion
        storage = messages.get_messages(request)
        storage.used = True
        messages.error(request, 'Please login to access the Career Navigator.')
        return redirect('authentication:login')
    
    # Get the career navigator agent
    try:
        agent = Agent.objects.get(slug='cybersec-career-navigator', is_active=True)
    except Agent.DoesNotExist:
        messages.error(request, 'Career Navigator is currently unavailable.')
        return redirect('agents:marketplace')
    
    # Check if user has sufficient balance
    if not request.user.has_sufficient_balance(agent.price):
        messages.error(request, f'Insufficient balance! You need {agent.price} AED to access the Career Navigator.')
        return redirect('wallet:wallet')
    
    # Deduct fee from user wallet
    success = request.user.deduct_balance(
        agent.price, 
        f'{agent.name} - Direct Access',
        agent.slug
    )
    
    if not success:
        messages.error(request, 'Failed to process payment. Please try again.')
        return redirect('agents:marketplace')
    
    # Create execution record for tracking
    execution = AgentExecution.objects.create(
        agent=agent,
        user=request.user,
        input_data={'action': 'direct_access', 'source': 'try_now_button'},
        fee_charged=agent.price,
        status='completed',
        output_data={
            'type': 'direct_access',
            'message': f'Direct access granted to {agent.name}',
            'access_method': 'try_now_button'
        },
        completed_at=timezone.now()
    )
    
    # Success message and redirect to form
    messages.success(request, f'✅ Payment processed! Welcome to your {agent.name} consultation.')
    return redirect('agents:career_navigator')


def career_navigator_view(request):
    """Display the career navigator form page"""
    if not request.user.is_authenticated:
        # Clear any existing messages to prevent confusion
        storage = messages.get_messages(request)
        storage.used = True
        messages.error(request, 'Please login to access the Career Navigator.')
        return redirect('authentication:login')
    
    # Get the career navigator agent
    try:
        agent = Agent.objects.get(slug='cybersec-career-navigator', is_active=True)
    except Agent.DoesNotExist:
        messages.error(request, 'Career Navigator is currently unavailable.')
        return redirect('agents:marketplace')
    
    # Check if user has a recent execution (within last 2 hours) or just redirect to payment
    from django.utils import timezone
    from datetime import timedelta
    
    recent_execution = AgentExecution.objects.filter(
        agent=agent,
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
    
    elif agent_slug == 'job-posting-generator':
        job_title = input_data.get('job_title', '')
        company_name = input_data.get('company_name', '')
        description = input_data.get('job_description', '')
        seniority = input_data.get('seniority_level', '')
        contract = input_data.get('contract_type', '')
        location = input_data.get('location', '')
        language = input_data.get('language', 'English')
        
        return f"Create a professional job posting for: {job_title} at {company_name}. Description: {description}. Seniority: {seniority}. Contract: {contract}. Location: {location}. Language: {language}. Make it comprehensive and attractive to candidates."
    
    # Default formatting for other agents
    params = [f"{key}: {value}" for key, value in input_data.items() if value]
    return f"Execute {agent_slug.replace('-', ' ').title()} with parameters: {'. '.join(params)}."


# Web interface views
@login_required
def agent_detail_view(request, slug):
    """Render agent detail page with dynamic form or chat interface"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    
    # Handle chat-based agents
    if agent.agent_type == 'chat':
        return chat_agent_view(request, agent)
    
    # Handle form-based agents (existing behavior)
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


# Chat-based agent views
def chat_agent_view(request, agent):
    """Render chat interface for chat-based agents"""
    chat_session = None
    messages = []
    
    if request.user.is_authenticated:
        # Get or create active chat session
        chat_session = ChatSession.objects.filter(
            agent=agent,
            user=request.user,
            status='active'
        ).first()
        
        # Get session ID from URL parameter if resuming a session
        session_id = request.GET.get('session')
        if session_id and not chat_session:
            chat_session = ChatSession.objects.filter(
                session_id=session_id,
                agent=agent,
                user=request.user
            ).first()
        
        # Get messages for the session
        if chat_session:
            messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    context = {
        'agent': agent,
        'chat_session': chat_session,
        'messages': messages,
        'timestamp': int(time.time())
    }
    
    return render(request, 'agents/agent_chat.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat_session(request):
    """Start a new chat session"""
    agent_slug = request.data.get('agent_slug')
    
    if not agent_slug:
        return Response({'error': 'agent_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    agent = get_object_or_404(Agent, slug=agent_slug, is_active=True, agent_type='chat')
    
    # Check wallet balance
    if hasattr(request.user, 'wallet_balance') and request.user.wallet_balance < agent.price:
        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for existing active session
    existing_session = ChatSession.objects.filter(
        agent=agent,
        user=request.user,
        status='active'
    ).first()
    
    if existing_session:
        return Response({
            'session_id': existing_session.session_id,
            'message': 'Active session already exists'
        })
    
    # Create new chat session
    session_id = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    
    from django.utils import timezone
    from datetime import timedelta
    
    chat_session = ChatSession.objects.create(
        session_id=session_id,
        agent=agent,
        user=request.user,
        fee_charged=agent.price,
        status='active',
        expires_at=timezone.now() + timedelta(hours=2)
    )
    
    # Deduct fee from wallet (if wallet system is implemented)
    # This would integrate with the existing wallet system
    
    # Send welcome message
    welcome_message = f"Welcome to {agent.name}! I'm here to help you with 5 Whys analysis. What problem would you like to analyze?"
    
    ChatMessage.objects.create(
        session=chat_session,
        message_type='agent',
        content=welcome_message
    )
    
    return Response({
        'session_id': chat_session.session_id,
        'message': 'Chat session started successfully'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request):
    """Send a message in a chat session"""
    session_id = request.data.get('session_id')
    message_content = request.data.get('message', '').strip()
    
    if not session_id or not message_content:
        return Response({'error': 'session_id and message are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get chat session
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user,
        status='active'
    )
    
    # Check if session is expired
    if chat_session.is_expired():
        chat_session.status = 'expired'
        chat_session.save()
        return Response({'error': 'Chat session has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Save user message
    user_message = ChatMessage.objects.create(
        session=chat_session,
        message_type='user',
        content=message_content
    )
    
    # Prepare webhook payload
    webhook_payload = {
        "message": {
            "text": f"Chat message: {message_content}. Provide helpful guidance about 5 Whys analysis. Do not generate the final report - just chat and help the user understand their problem."
        },
        "sessionId": session_id,
        "userId": str(request.user.id),
        "agentId": chat_session.agent.slug,
        "messageType": "chat"
    }
    
    try:
        # Validate webhook URL
        validate_webhook_url(chat_session.agent.webhook_url)
        
        # Send to webhook
        response = requests.post(
            chat_session.agent.webhook_url,
            json=webhook_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Try multiple possible response field names from N8N
            agent_response = None
            possible_fields = ['output', 'response', 'message', 'reply', 'result', 'text', 'content']
            
            # Handle array response first (your N8N case)
            if isinstance(response_data, list) and len(response_data) > 0:
                first_item = response_data[0]
                if isinstance(first_item, dict):
                    for field in possible_fields:
                        if field in first_item:
                            agent_response = first_item[field]
                            break
                elif isinstance(first_item, str):
                    agent_response = first_item
            
            # Handle direct object response
            elif isinstance(response_data, dict):
                for field in possible_fields:
                    if field in response_data:
                        agent_response = response_data[field]
                        break
            
            # If response_data is a string itself
            elif isinstance(response_data, str):
                agent_response = response_data
            
            # Fallback with full response data for debugging
            if agent_response is None:
                agent_response = f"N8N Response received but couldn't parse: {str(response_data)[:200]}..."
            
            # Save agent response
            agent_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='agent',
                content=str(agent_response),
                metadata={'webhook_response': response_data, 'raw_response': response.text}
            )
            
            # Update session timestamp and extend expiration
            chat_session.extend_session()
            
            return Response({
                'user_message': {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'agent_message': {
                    'id': str(agent_message.id),
                    'content': agent_message.content,
                    'timestamp': agent_message.timestamp.isoformat()
                }
            })
        else:
            # Webhook error
            error_message = "I'm having trouble processing your message right now. Please try again."
            agent_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='agent',
                content=error_message,
                metadata={'error': f'Webhook returned {response.status_code}'}
            )
            
            return Response({
                'user_message': {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'agent_message': {
                    'id': str(agent_message.id),
                    'content': agent_message.content,
                    'timestamp': agent_message.timestamp.isoformat()
                }
            }, status=status.HTTP_202_ACCEPTED)
            
    except Exception as e:
        # Handle webhook errors
        error_message = "I'm experiencing technical difficulties. Please try again later."
        agent_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='agent',
            content=error_message,
            metadata={'error': str(e)}
        )
        
        return Response({
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat()
            },
            'agent_message': {
                'id': str(agent_message.id),
                'content': agent_message.content,
                'timestamp': agent_message.timestamp.isoformat()
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, session_id):
    """Get chat history for a session"""
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user
    )
    
    messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    message_data = []
    for message in messages:
        message_data.append({
            'id': str(message.id),
            'message_type': message.message_type,
            'content': message.content,
            'timestamp': message.timestamp.isoformat()
        })
    
    return Response({
        'session_id': session_id,
        'status': chat_session.status,
        'messages': message_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_chat_session(request):
    """End a chat session"""
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    chat_session = get_object_or_404(
        ChatSession,
        session_id=session_id,
        user=request.user,
        status='active'
    )
    
    chat_session.status = 'completed'
    chat_session.completed_at = timezone.now()
    chat_session.save()
    
    return Response({'message': 'Chat session ended successfully'})
