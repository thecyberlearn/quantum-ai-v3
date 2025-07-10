from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .models import User


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect to 'next' parameter if provided, otherwise homepage
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:homepage')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'authentication/login.html')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'authentication/register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('core:homepage')
        except Exception as e:
            messages.error(request, 'Error creating account')
    
    return render(request, 'authentication/register.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('core:homepage')


@login_required
def profile_view(request):
    """User profile view"""
    # Get all transactions first (not sliced)
    all_transactions = request.user.wallet_transactions.all()
    
    # Get recent transactions (sliced for display)
    transactions = all_transactions[:50]
    
    # Calculate usage statistics using all transactions
    total_spent = sum(abs(t.amount) for t in all_transactions if t.type == 'agent_usage')
    total_topped_up = sum(t.amount for t in all_transactions if t.type == 'top_up')
    total_agents_used = all_transactions.filter(type='agent_usage').count()
    
    # Get most used agents
    from django.db.models import Count
    popular_agents = (all_transactions.filter(type='agent_usage')
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
    
    return render(request, 'authentication/profile.html', context)
