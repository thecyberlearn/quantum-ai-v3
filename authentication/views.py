from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import User, PasswordResetToken


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


def forgot_password_view(request):
    """Forgot password view - request password reset"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Create password reset token
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # Build reset URL using correct site URL
            reset_path = reverse('authentication:reset_password', kwargs={'token': reset_token.token})
            reset_url = f"{settings.SITE_URL}{reset_path}"
            
            # Send email
            subject = 'Password Reset Request'
            message = f'''
Hello {user.username},

You requested a password reset for your NetCop account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
NetCop Team
            '''
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset instructions have been sent to your email.')
                
                # Log successful email for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Password reset email sent successfully to {email}")
                
            except Exception as e:
                # Log the actual error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                
                messages.error(request, f'Failed to send reset email: {str(e)}')
                
        except User.DoesNotExist:
            # Show helpful error message for better UX
            messages.error(request, f'No account found with email {email}. Please check your email address or create a new account.')
    
    return render(request, 'authentication/forgot_password.html')


def reset_password_view(request, token):
    """Reset password view - using token from email"""
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired or is invalid.')
        return redirect('authentication:forgot_password')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/reset_password.html', {'token': token})
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'authentication/reset_password.html', {'token': token})
        
        # Reset password
        user = reset_token.user
        user.set_password(password1)
        user.save()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        messages.success(request, 'Your password has been reset successfully. You can now log in.')
        return redirect('authentication:login')
    
    return render(request, 'authentication/reset_password.html', {'token': token})
