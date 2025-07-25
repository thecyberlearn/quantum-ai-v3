from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
from django_ratelimit.exceptions import Ratelimited
from .models import User, PasswordResetToken, EmailVerificationToken
import logging

logger = logging.getLogger(__name__)


def validate_password_strength(password):
    """Validate password strength on backend"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    common_passwords = ['password', '12345678', 'qwerty', 'abc123', 'password123', '123456789']
    if password.lower() in common_passwords:
        errors.append("Password is too common and easily guessable")
    
    return errors


def send_verification_email(user):
    """Send email verification to new user"""
    try:
        # Create verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Build verification URL
        verification_path = reverse('authentication:verify_email', kwargs={'token': verification_token.token})
        verification_url = f"{settings.SITE_URL}{verification_path}"
        
        # Send email
        subject = 'Verify Your Email Address - Quantum Tasks AI'
        message = f'''
Hello {user.username},

Welcome to Quantum Tasks AI! Please verify your email address to complete your account setup.

Click the link below to verify your email:
{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Quantum Tasks AI Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def handle_ratelimited(request, exception):
    """Custom handler for rate limited requests"""
    logger.warning(f"Rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
    messages.error(request, 'Too many attempts. Please try again in a few minutes.')
    return render(request, 'authentication/login.html')


@ratelimit(key='ip', rate='5/m', method=UNSAFE, block=False)
def login_view(request):
    """User login view with rate limiting (5 attempts per minute per IP)"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Login rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many login attempts. Please try again in a few minutes.')
        return render(request, 'authentication/login.html')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Check if email is verified
            if not user.email_verified:
                messages.warning(request, 'Please verify your email address before logging in. Check your inbox for the verification link.')
                return render(request, 'authentication/login.html')
            
            login(request, user)
            # Redirect to 'next' parameter if provided, otherwise homepage
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:homepage')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'authentication/login.html')


@ratelimit(key='ip', rate='3/m', method=UNSAFE, block=False)
def register_view(request):
    """User registration view with rate limiting (3 attempts per minute per IP)"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Registration rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many registration attempts. Please try again in a few minutes.')
        return render(request, 'authentication/register.html')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/register.html')
        
        # Validate password strength
        password_errors = validate_password_strength(password1)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
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
            # Don't automatically login - require email verification first
            
            # Send verification email
            if send_verification_email(user):
                messages.success(request, 'Account created successfully! Please check your email to verify your account.')
            else:
                messages.warning(request, 'Account created but verification email could not be sent. You can request a new one after logging in.')
            
            return redirect('authentication:login')
        except Exception as e:
            logger.error(f"Error creating account for {email}: {str(e)}")
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


@ratelimit(key='ip', rate='3/5m', method=UNSAFE, block=False)
def forgot_password_view(request):
    """Forgot password view with rate limiting (3 attempts per 5 minutes per IP)"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Password reset rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many password reset attempts. Please try again in a few minutes.')
        return render(request, 'authentication/forgot_password.html')
    
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
                messages.success(request, 'If an account with that email exists, password reset instructions have been sent.')
                
                # Log successful email for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Password reset email sent successfully to {email}")
                
            except Exception as e:
                # Log the actual error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                
                messages.error(request, 'Unable to send reset email at this time. Please try again later.')
                
        except User.DoesNotExist:
            # Log the attempt for security monitoring but show generic message
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            # Show same success message to prevent user enumeration
            messages.success(request, 'If an account with that email exists, password reset instructions have been sent.')
    
    return render(request, 'authentication/forgot_password.html')


@ratelimit(key='ip', rate='3/5m', method=UNSAFE, block=True)
def reset_password_view(request, token):
    """Reset password view with rate limiting (3 attempts per 5 minutes per IP)"""
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
        
        # Validate password strength
        password_errors = validate_password_strength(password1)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
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


def verify_email_view(request, token):
    """Email verification view"""
    verification_token = get_object_or_404(EmailVerificationToken, token=token)
    
    if not verification_token.is_valid():
        messages.error(request, 'This verification link has expired or is invalid.')
        return redirect('authentication:login')
    
    # Mark email as verified
    user = verification_token.user
    user.email_verified = True
    user.save()
    
    # Mark token as used
    verification_token.mark_as_used()
    
    messages.success(request, 'Email verified successfully! You can now log in.')
    return redirect('authentication:login')


@ratelimit(key='ip', rate='2/5m', method=UNSAFE, block=False)
def resend_verification_view(request):
    """Resend email verification"""
    # Check if rate limited
    if getattr(request, 'limited', False):
        logger.warning(f"Verification resend rate limit exceeded for IP {request.META.get('REMOTE_ADDR')}")
        messages.error(request, 'Too many verification requests. Please try again in a few minutes.')
        return redirect('authentication:login')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                messages.info(request, 'Your email is already verified. You can log in.')
                return redirect('authentication:login')
            
            # Send new verification email
            if send_verification_email(user):
                messages.success(request, 'Verification email sent. Please check your inbox.')
            else:
                messages.error(request, 'Unable to send verification email at this time.')
            
        except User.DoesNotExist:
            # Show same success message to prevent user enumeration
            messages.success(request, 'If an account with that email exists, a verification email has been sent.')
    
    return render(request, 'authentication/resend_verification.html')
