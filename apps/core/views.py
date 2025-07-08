# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from agents.models import Agent
from agents.agent_processors import AgentProcessor
import json
import os

User = get_user_model()

def homepage(request):
    """Enhanced homepage with all features from Next.js version"""
    # Handle contact form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        company = request.POST.get('company', '')
        message = request.POST.get('message')
        
        if name and email and message:
            # Here you can save to database or send email
            # For now, just show success message
            messages.success(request, f'Thank you {name}! Your message has been sent. We will get back to you soon.')
            return redirect('homepage')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get featured agents for preview
    featured_agents = Agent.objects.filter(is_active=True)[:3]
    
    context = {
        'featured_agents': featured_agents,
        'total_agents': Agent.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
    }
    
    return render(request, 'homepage.html', context)

def marketplace(request):
    """Display all available agents with enhanced filtering"""
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    
    agents = Agent.objects.filter(is_active=True)
    
    if category_filter:
        agents = agents.filter(category=category_filter)
    
    if search_query:
        from django.db import models
        agents = agents.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Get unique categories for filter dropdown
    categories = Agent.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    
    context = {
        'agents': agents.order_by('category', 'name'),
        'categories': categories,
        'current_category': category_filter,
        'search_query': search_query,
    }
    
    return render(request, 'marketplace.html', context)

def pricing(request):
    """Enhanced pricing page with payment status handling"""
    packages = [
        {
            'id': 'basic', 
            'amount': 10, 
            'price': 9.99, 
            'label': 'Basic',
            'description': 'Perfect for trying out AI agents',
            'features': ['2-4 agent uses', 'Basic support', 'Email notifications'],
            'icon': '💰',
            'gradient': 'from-blue-500 to-purple-600'
        },
        {
            'id': 'popular', 
            'amount': 50, 
            'price': 49.99, 
            'label': 'Popular',
            'description': 'Most popular choice for regular users',
            'features': ['10-25 agent uses', 'Priority support', 'Advanced analytics', 'Export options'],
            'icon': '⭐',
            'gradient': 'from-purple-500 to-pink-600',
            'popular': True
        },
        {
            'id': 'premium', 
            'amount': 100, 
            'price': 99.99, 
            'label': 'Premium',
            'description': 'For power users and small teams',
            'features': ['50+ agent uses', '24/7 support', 'Custom integrations', 'Team collaboration'],
            'icon': '🚀',
            'gradient': 'from-green-500 to-teal-600'
        },
        {
            'id': 'enterprise', 
            'amount': 500, 
            'price': 499.99, 
            'label': 'Enterprise',
            'description': 'For large teams and businesses',
            'features': ['Unlimited uses', 'Dedicated support', 'Custom development', 'SLA guarantee'],
            'icon': '👑',
            'gradient': 'from-yellow-500 to-red-600'
        },
    ]
    
    # Handle payment status messages (prevent duplicate messages)
    payment_status = request.GET.get('payment')
    session_id = request.GET.get('session_id')
    
    # Create session key to prevent duplicate messages
    if payment_status:
        session_key = f"payment_message_{payment_status}_{session_id or 'cancelled'}"
        if not request.session.get(session_key):
            request.session[session_key] = True
            
            if payment_status == 'success':
                messages.success(request, '✅ Payment successful! Your wallet has been topped up.')
            elif payment_status == 'cancelled':
                messages.error(request, '❌ Payment was cancelled. No charges were made.')
    
    # FAQ data
    faqs = [
        {
            'question': 'How does the pay-per-use pricing work?',
            'answer': 'You add money to your wallet and pay for each AI agent use. Prices range from 2.00 to 8.00 AED per use.'
        },
        {
            'question': 'Do wallet funds expire?',
            'answer': 'No, your wallet balance never expires. Use it whenever you need AI assistance.'
        },
        {
            'question': 'Can I get a refund?',
            'answer': 'Yes, unused wallet balance can be refunded within 30 days of purchase.'
        },
        {
            'question': 'Is my payment information secure?',
            'answer': 'Absolutely. We use Stripe for secure payment processing and never store your payment details.'
        }
    ]
    
    context = {
        'packages': packages,
        'faqs': faqs,
    }
    
    return render(request, 'pricing.html', context)

def debug_page(request):
    """Debug page for development environment checking"""
    if not settings.DEBUG:
        context = {'debug_mode': False}
        return render(request, 'debug.html', context)
    
    # Environment status check
    env_status = {
        'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
        'STRIPE_SECRET_KEY': bool(settings.STRIPE_SECRET_KEY),
        'N8N_WEBHOOK_DATA_ANALYZER': bool(settings.N8N_WEBHOOK_DATA_ANALYZER),
        'N8N_WEBHOOK_FIVE_WHYS': bool(settings.N8N_WEBHOOK_FIVE_WHYS),
        'OPENWEATHER_API_KEY': bool(settings.OPENWEATHER_API_KEY),
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
    }
    
    # Database connection test
    try:
        user_count = User.objects.count()
        agent_count = Agent.objects.count()
        db_status = {'status': 'Connected', 'color': 'green'}
    except Exception as e:
        user_count = 0
        agent_count = 0
        db_status = {'status': f'Error: {str(e)}', 'color': 'red'}
    
    context = {
        'debug_mode': True,
        'env_status': json.dumps(env_status, indent=2),
        'db_status': db_status,
        'user_count': user_count,
        'agent_count': agent_count,
    }
    
    return render(request, 'debug.html', context)

def reset_password(request):
    """Password reset functionality"""
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not password or not confirm_password:
            context = {'error': 'Both password fields are required'}
            return render(request, 'reset_password.html', context)
        
        if password != confirm_password:
            context = {'error': 'Passwords do not match'}
            return render(request, 'reset_password.html', context)
        
        if len(password) < 8:
            context = {'error': 'Password must be at least 8 characters long'}
            return render(request, 'reset_password.html', context)
        
        # In a real implementation, you would:
        # 1. Verify the reset token from the URL
        # 2. Update the user's password
        # 3. Redirect to login with success message
        
        messages.success(request, 'Password updated successfully! Please log in with your new password.')
        return redirect('homepage')
    
    # Check if we have a valid reset token (simplified version)
    token = request.GET.get('token')
    if not token:
        context = {'error': 'Invalid or expired reset link. Please request a new password reset.'}
        return render(request, 'reset_password.html', context)
    
    return render(request, 'reset_password.html')

@login_required
def agent_detail(request, slug):
    """Enhanced agent detail page with wallet balance checking"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    
    # Calculate wallet status
    user_balance = request.user.wallet_balance
    has_sufficient_balance = user_balance >= agent.price
    
    # Calculate usage count
    if has_sufficient_balance:
        possible_uses = int(user_balance / agent.price)
    else:
        possible_uses = 0
    
    context = {
        'agent': agent,
        'user_balance': user_balance,
        'has_sufficient_balance': has_sufficient_balance,
        'possible_uses': possible_uses,
        'balance_after_use': user_balance - agent.price if has_sufficient_balance else user_balance,
    }
    
    return render(request, 'agent_detail.html', context)

@login_required
@require_http_methods(["POST"])
def process_agent(request, slug):
    """Enhanced agent processing with comprehensive error handling"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    
    # Check wallet balance
    if not request.user.has_sufficient_balance(agent.price):
        return JsonResponse({
            'success': False,
            'error': f'Insufficient balance. Required: {agent.price_display}, Available: {request.user.wallet_balance:.2f} AED'
        }, status=400)
    
    try:
        # Process based on agent type
        processor = AgentProcessor(agent.slug)
        
        if agent.slug == 'data-analyzer':
            file_obj = request.FILES.get('file')
            if not file_obj:
                return JsonResponse({'success': False, 'error': 'File is required'}, status=400)
            
            # Validate file size (10MB limit)
            if file_obj.size > 10 * 1024 * 1024:
                return JsonResponse({'success': False, 'error': 'File size must be less than 10MB'}, status=400)
            
            # Validate file type
            allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
            file_extension = os.path.splitext(file_obj.name)[1].lower()
            if file_extension not in allowed_extensions:
                return JsonResponse({'success': False, 'error': 'Invalid file type. Allowed: CSV, Excel, JSON'}, status=400)
            
            result = processor.process_agent(file_obj=file_obj, user_id=str(request.user.id))
        
        elif agent.slug == 'five-whys':
            problem = request.POST.get('problem')
            if not problem or len(problem.strip()) < 10:
                return JsonResponse({'success': False, 'error': 'Problem description must be at least 10 characters'}, status=400)
            result = processor.process_agent(problem_description=problem, user_id=str(request.user.id))
        
        elif agent.slug == 'weather-reporter':
            location = request.POST.get('location')
            if not location or len(location.strip()) < 2:
                return JsonResponse({'success': False, 'error': 'Location must be at least 2 characters'}, status=400)
            result = processor.process_agent(location=location)
        
        elif agent.slug == 'job-posting-generator':
            required_fields = ['title', 'company', 'description', 'requirements']
            job_details = {}
            
            for field in required_fields:
                value = request.POST.get(field, '').strip()
                if not value:
                    return JsonResponse({'success': False, 'error': f'{field.title()} is required'}, status=400)
                if len(value) < 5:
                    return JsonResponse({'success': False, 'error': f'{field.title()} must be at least 5 characters'}, status=400)
                job_details[field] = value
            
            result = processor.process_agent(job_details=job_details, user_id=str(request.user.id))
        
        elif agent.slug == 'social-ads-generator':
            required_fields = ['product', 'platform', 'target_audience', 'tone']
            ad_requirements = {}
            
            for field in required_fields:
                value = request.POST.get(field, '').strip()
                if not value:
                    return JsonResponse({'success': False, 'error': f'{field.replace("_", " ").title()} is required'}, status=400)
                ad_requirements[field] = value
            
            # Validate platform
            valid_platforms = ['facebook', 'instagram', 'twitter', 'linkedin']
            if ad_requirements['platform'] not in valid_platforms:
                return JsonResponse({'success': False, 'error': 'Invalid platform selected'}, status=400)
            
            # Validate tone
            valid_tones = ['professional', 'casual', 'humorous', 'urgent']
            if ad_requirements['tone'] not in valid_tones:
                return JsonResponse({'success': False, 'error': 'Invalid tone selected'}, status=400)
            
            result = processor.process_agent(ad_requirements=ad_requirements, user_id=str(request.user.id))
        
        elif agent.slug == 'faq-generator':
            content_source = request.POST.get('content_source', '').strip()
            if not content_source:
                return JsonResponse({'success': False, 'error': 'Content source is required'}, status=400)
            if len(content_source) < 50:
                return JsonResponse({'success': False, 'error': 'Content source must be at least 50 characters'}, status=400)
            
            result = processor.process_agent(content_source=content_source, user_id=str(request.user.id))
        
        else:
            return JsonResponse({'success': False, 'error': 'Agent not supported'}, status=400)
        
        # Deduct balance on successful processing
        if request.user.deduct_balance(
            agent.price, 
            f"Used {agent.name}",
            agent.slug
        ):
            return JsonResponse({
                'success': True,
                'result': result,
                'new_balance': float(request.user.wallet_balance),
                'agent_used': agent.name,
                'cost': float(agent.price)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to process payment. Please try again.'
            }, status=400)
    
    except Exception as e:
        # Log the error in production
        if not settings.DEBUG:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Agent processing error: {str(e)}", exc_info=True)
        
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request. Please try again later.'
        }, status=500)

@login_required
def profile(request):
    """Enhanced user profile with transaction history and wallet management"""
    # Get recent transactions
    transactions = request.user.wallet_transactions.all()[:50]  # Last 50 transactions
    
    # Calculate usage statistics
    total_spent = sum(abs(t.amount) for t in transactions if t.type == 'agent_usage')
    total_topped_up = sum(t.amount for t in transactions if t.type == 'top_up')
    total_agents_used = transactions.filter(type='agent_usage').count()
    
    # Get most used agents
    from django.db.models import Count
    popular_agents = (transactions.filter(type='agent_usage')
                     .values('agent_slug')
                     .annotate(count=Count('agent_slug'))
                     .order_by('-count')[:5])
    
    # Wallet status
    balance = request.user.wallet_balance
    if balance < 5:
        wallet_status = {'status': 'low', 'color': 'red', 'message': 'Low balance - Add money to continue using agents'}
    elif balance < 20:
        wallet_status = {'status': 'medium', 'color': 'orange', 'message': 'Consider adding more funds'}
    else:
        wallet_status = {'status': 'high', 'color': 'green', 'message': 'Good balance'}
    
    context = {
        'transactions': transactions,
        'total_spent': total_spent,
        'total_topped_up': total_topped_up,
        'total_agents_used': total_agents_used,
        'popular_agents': popular_agents,
        'wallet_status': wallet_status,
    }
    
    return render(request, 'profile.html', context)

# API endpoints for AJAX functionality
@login_required
@require_http_methods(["GET"])
def check_wallet_balance(request):
    """API endpoint to check current wallet balance"""
    return JsonResponse({
        'balance': float(request.user.wallet_balance),
        'formatted_balance': f"{request.user.wallet_balance:.2f} AED"
    })

@login_required
@require_http_methods(["POST"])
def chat_message(request, slug):
    """Handle chat messages for interactive agents like 5 Whys"""
    if slug != 'five-whys':
        return JsonResponse({'success': False, 'error': 'Chat not available for this agent'}, status=400)
    
    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
    
    # Here you would integrate with your 5 Whys processing logic
    # For now, return a simple response
    response_message = f"Thank you for: {message}. Let me ask you the next Why question..."
    
    return JsonResponse({
        'success': True,
        'response': response_message,
        'timestamp': timezone.now().isoformat()
    })

