# 💳 NetCop Wallet/Stripe Implementation Guide

## 🎯 Overview
This guide documents how to implement a professional wallet system with Stripe Payment Intents API in the NetCop Django project. The system provides real-time payment processing **without requiring webhooks** for basic functionality.

## ✨ Key Features
- **Professional wallet topup interface** with Stripe Elements
- **Real-time payment processing** with Payment Intents API
- **Loading states and progress indicators** for better UX
- **Webhook-free operation** for development and testing
- **AED currency support** matching NetCop pricing
- **Balance checking** before agent usage
- **Transaction history** with copy/download functionality

## 🚫 No Webhooks Required

### Why No Webhooks Needed:
- **Payment Intents API** provides immediate payment status
- **Frontend confirmation** happens in real-time after card processing
- **Direct database updates** via confirmed payment status
- **Duplicate prevention** through payment metadata checking

### Payment Flow (Webhook-Free):
1. User selects topup amount → Frontend creates Payment Intent
2. Stripe Elements processes card securely → Returns success/failure
3. Frontend confirms payment status → Backend updates wallet immediately
4. User sees updated balance → Can use agents with sufficient funds

---

## 🏗️ Implementation Steps

### 1. Environment Configuration

Add to `.env` file:
```bash
# Stripe Configuration (No webhook secret required for basic functionality)
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
# STRIPE_WEBHOOK_SECRET=whsec_... (optional for production)
```

Add to `netcop_hub/settings.py`:
```python
# Stripe Configuration
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')
```

### 2. User Model Enhancement

Update `authentication/models.py` to add wallet balance:
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

class User(AbstractUser):
    email = models.EmailField(unique=True)
    wallet_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="User wallet balance in AED"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def has_sufficient_balance(self, amount):
        """Check if user has sufficient balance for a transaction"""
        return self.wallet_balance >= Decimal(str(amount))
    
    def deduct_balance(self, amount, description=""):
        """Deduct amount from wallet balance"""
        if self.has_sufficient_balance(amount):
            self.wallet_balance -= Decimal(str(amount))
            self.save()
            
            # Create transaction record
            from wallet.models import WalletTransaction
            WalletTransaction.objects.create(
                user=self,
                amount=-Decimal(str(amount)),
                type='agent_usage',
                description=description
            )
            return True
        return False
    
    def add_balance(self, amount, description=""):
        """Add amount to wallet balance"""
        self.wallet_balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        from wallet.models import WalletTransaction
        WalletTransaction.objects.create(
            user=self,
            amount=Decimal(str(amount)),
            type='top_up',
            description=description
        )
```

### 3. Wallet Models

Update `wallet/models.py`:
```python
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('top_up', 'Top Up'),
        ('agent_usage', 'Agent Usage'),
        ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField()
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} AED ({self.type})"
```

### 4. Wallet Views (Payment Intents API)

Create `wallet/views.py`:
```python
import stripe
import json
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import WalletTransaction
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def topup(request):
    """Professional wallet topup page"""
    return render(request, "wallet/topup.html", {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'user_balance': request.user.wallet_balance
    })

@login_required
@csrf_exempt
def create_payment_intent(request):
    """Create Stripe Payment Intent for wallet topup"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = int(data.get("amount"))
            
            if amount < 1:
                return JsonResponse({"error": "Amount must be at least 1 AED"}, status=400)
            
            # Create Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=amount * 100,  # Convert to fils (AED cents)
                currency='aed',
                metadata={
                    'user_id': request.user.id,
                    'amount': amount,
                    'email': request.user.email
                },
                description=f"NetCop wallet top-up for {request.user.email}"
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'amount': amount
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
@csrf_exempt
def confirm_payment(request):
    """Confirm payment and update wallet balance"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get("payment_intent_id")
            
            # Retrieve payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                user_id = int(intent.metadata['user_id'])
                amount = Decimal(intent.metadata['amount'])
                
                # Verify this is the correct user
                if user_id != request.user.id:
                    return JsonResponse({"error": "Unauthorized"}, status=403)
                
                # Check for duplicate processing
                existing_transaction = WalletTransaction.objects.filter(
                    stripe_payment_intent_id=payment_intent_id
                ).first()
                
                if not existing_transaction:
                    # Update user balance using model method
                    request.user.add_balance(
                        amount=amount,
                        description=f"Wallet top-up via Stripe - {amount} AED"
                    )
                    
                    # Update the transaction with Stripe ID
                    latest_transaction = WalletTransaction.objects.filter(
                        user=request.user,
                        type='top_up',
                        amount=amount
                    ).first()
                    if latest_transaction:
                        latest_transaction.stripe_payment_intent_id = payment_intent_id
                        latest_transaction.save()
                
                return JsonResponse({
                    "success": True,
                    "message": f"Successfully added {amount} AED to your wallet",
                    "new_balance": str(request.user.wallet_balance)
                })
            else:
                return JsonResponse({"error": "Payment not completed"}, status=400)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
def transaction_history(request):
    """View transaction history"""
    transactions = request.user.wallet_transactions.all()[:50]
    return render(request, "wallet/history.html", {
        'transactions': transactions,
        'current_balance': request.user.wallet_balance
    })
```

### 5. Wallet URLs

Create `wallet/urls.py`:
```python
from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.topup, name='topup'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('history/', views.transaction_history, name='history'),
]
```

### 6. Professional Topup Template

Create `templates/wallet/topup.html`:
```html
{% extends 'base.html' %}

{% block title %}Top Up Wallet - NetCop Hub{% endblock %}

{% block content %}
<div style="max-width: 600px; margin: var(--space-xl) auto; padding: 0 var(--space-md);">
    <div class="card">
        <div style="text-align: center; margin-bottom: var(--space-xl);">
            <h1 style="color: var(--text-primary); margin-bottom: var(--space-sm);">💰 Top Up Wallet</h1>
            <p style="color: var(--text-secondary);">Add funds to your wallet to use AI agents</p>
        </div>
        
        <div style="background: var(--bg-accent); padding: var(--space-md); border-radius: var(--radius); margin-bottom: var(--space-lg); text-align: center;">
            <p style="color: var(--text-secondary); margin-bottom: var(--space-xs);">Current Balance</p>
            <p style="font-size: var(--text-xl); font-weight: 600; color: var(--success-green);">
                {{ user_balance|floatformat:2 }} AED
            </p>
        </div>

        <!-- Amount Selection -->
        <div style="margin-bottom: var(--space-lg);">
            <label style="display: block; font-weight: 500; color: var(--text-primary); margin-bottom: var(--space-sm);">Select Amount (AED)</label>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-sm); margin-bottom: var(--space-md);">
                <button type="button" class="btn btn-secondary amount-btn" data-amount="50">50 AED</button>
                <button type="button" class="btn btn-secondary amount-btn" data-amount="100">100 AED</button>
                <button type="button" class="btn btn-secondary amount-btn" data-amount="200">200 AED</button>
            </div>
            <input type="number" 
                   id="amount" 
                   placeholder="Enter custom amount"
                   class="form-input" 
                   style="width: 100%;"
                   min="1" 
                   required>
        </div>

        <!-- Payment Form -->
        <form id="payment-form">
            <div style="margin-bottom: var(--space-lg);">
                <label style="display: block; font-weight: 500; color: var(--text-primary); margin-bottom: var(--space-sm);">💳 Card Information</label>
                <div id="card-element" style="border: 1px solid var(--border-color); border-radius: var(--radius); padding: var(--space-md); background: var(--bg-primary);">
                    <!-- Stripe Elements will create form elements here -->
                </div>
                <div id="card-errors" style="color: var(--error-red); font-size: var(--text-sm); margin-top: var(--space-sm);" role="alert"></div>
            </div>

            <button id="submit-payment" 
                    type="submit" 
                    class="btn btn-primary"
                    style="width: 100%; font-size: var(--text-base);">
                <span id="button-text">🚀 Add to Wallet</span>
                <div id="spinner" style="display: none;">
                    <span style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ffffff; border-radius: 50%; border-top-color: transparent; animation: spin 1s linear infinite; margin-right: var(--space-xs);"></span>
                    Processing...
                </div>
            </button>
        </form>

        <!-- Success/Error Messages -->
        <div id="payment-result" style="margin-top: var(--space-lg); display: none;">
            <div id="success-message" style="background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: var(--space-md); border-radius: var(--radius); display: none;">
                <strong>✅ Success!</strong> <span id="success-text"></span>
            </div>
            <div id="error-message" style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: var(--space-md); border-radius: var(--radius); display: none;">
                <strong>❌ Error:</strong> <span id="error-text"></span>
            </div>
        </div>
    </div>
</div>

<!-- Stripe.js -->
<script src="https://js.stripe.com/v3/"></script>
<script>
    // CSS for spinner animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Initialize Stripe
    const stripe = Stripe('{{ stripe_publishable_key }}');
    const elements = stripe.elements();

    // Create card element
    const cardElement = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                color: '#1f2937',
                fontFamily: 'Inter, system-ui, sans-serif',
                '::placeholder': {
                    color: '#9ca3af',
                },
            },
            invalid: {
                color: '#dc2626',
            },
        },
    });

    cardElement.mount('#card-element');

    // Handle real-time validation errors
    cardElement.addEventListener('change', ({error}) => {
        const displayError = document.getElementById('card-errors');
        if (error) {
            displayError.textContent = error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // Amount selection buttons
    document.querySelectorAll('.amount-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const amount = this.dataset.amount;
            document.getElementById('amount').value = amount;
            
            // Update button styles
            document.querySelectorAll('.amount-btn').forEach(b => {
                b.classList.remove('btn-primary');
                b.classList.add('btn-secondary');
            });
            this.classList.remove('btn-secondary');
            this.classList.add('btn-primary');
        });
    });

    // Payment form submission
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const amount = parseInt(document.getElementById('amount').value);
        if (!amount || amount < 1) {
            showError('Please enter a valid amount');
            return;
        }

        setLoading(true);

        try {
            // Create Payment Intent
            const response = await fetch('/wallet/create-payment-intent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount: amount }),
            });

            const { client_secret, error } = await response.json();

            if (error) {
                showError(error);
                setLoading(false);
                return;
            }

            // Confirm payment with Stripe
            const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
                payment_method: {
                    card: cardElement,
                }
            });

            if (stripeError) {
                showError(stripeError.message);
                setLoading(false);
            } else if (paymentIntent.status === 'succeeded') {
                // Confirm payment on server
                const confirmResponse = await fetch('/wallet/confirm-payment/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ payment_intent_id: paymentIntent.id }),
                });

                const confirmResult = await confirmResponse.json();

                if (confirmResult.success) {
                    showSuccess(`${confirmResult.message}. New balance: ${confirmResult.new_balance} AED`);
                    // Reset form
                    form.reset();
                    cardElement.clear();
                    document.getElementById('amount').value = '';
                    // Reset amount buttons
                    document.querySelectorAll('.amount-btn').forEach(b => {
                        b.classList.remove('btn-primary');
                        b.classList.add('btn-secondary');
                    });
                    // Reload page after 2 seconds to show updated balance
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    showError(confirmResult.error || 'Payment confirmation failed');
                }
                setLoading(false);
            }
        } catch (error) {
            showError('Network error: ' + error.message);
            setLoading(false);
        }
    });

    function setLoading(loading) {
        const button = document.getElementById('submit-payment');
        const buttonText = document.getElementById('button-text');
        const spinner = document.getElementById('spinner');

        if (loading) {
            button.disabled = true;
            buttonText.style.display = 'none';
            spinner.style.display = 'inline-block';
        } else {
            button.disabled = false;
            buttonText.style.display = 'inline-block';
            spinner.style.display = 'none';
        }
    }

    function showSuccess(message) {
        const resultDiv = document.getElementById('payment-result');
        const successDiv = document.getElementById('success-message');
        const errorDiv = document.getElementById('error-message');
        const successText = document.getElementById('success-text');

        successText.textContent = message;
        successDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        resultDiv.style.display = 'block';
    }

    function showError(message) {
        const resultDiv = document.getElementById('payment-result');
        const successDiv = document.getElementById('success-message');
        const errorDiv = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');

        errorText.textContent = message;
        errorDiv.style.display = 'block';
        successDiv.style.display = 'none';
        resultDiv.style.display = 'block';
    }
</script>
{% endblock %}
```

### 7. Update Navigation

Update `templates/base.html` to include wallet balance in navigation:
```html
<!-- In the user info section -->
{% if user.is_authenticated %}
    <p class="user-welcome">Welcome, {{ user.username }}!</p>
    <a href="{% url 'wallet:topup' %}" class="balance" data-wallet-balance>💰 {{ user.wallet_balance|floatformat:2 }} AED</a>
    <div class="auth-links">
        <a href="{% url 'wallet:topup' %}">Wallet</a>
        <a href="{% url 'authentication:logout' %}">Logout</a>
    </div>
{% endif %}
```

### 8. Update Main URLs

Add wallet URLs to `netcop_hub/urls.py`:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('wallet/', include('wallet.urls')),  # Add this line
    # ... other URLs
]
```

---

## 🧪 Testing Guide

### 1. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Test with Stripe Test Cards
- **Successful payment**: `4242 4242 4242 4242`
- **Requires authentication**: `4000 0025 0000 3155`
- **Declined card**: `4000 0000 0000 9995`

### 3. Testing Checklist
- [ ] User can access wallet topup page
- [ ] Amount selection buttons work
- [ ] Card form validates properly
- [ ] Payment processing shows loading states
- [ ] Successful payments update balance immediately
- [ ] Failed payments show error messages
- [ ] Balance displays in navigation
- [ ] Transaction history is recorded

---

## 🚀 Advanced Features (Optional)

### Agent Integration
Update agent views to check wallet balance:
```python
@login_required
def use_agent(request, agent_slug):
    agent = get_object_or_404(BaseAgent, slug=agent_slug)
    
    if not request.user.has_sufficient_balance(agent.price):
        return JsonResponse({
            'error': f'Insufficient balance. Need {agent.price} AED.',
            'redirect_url': reverse('wallet:topup')
        }, status=400)
    
    # Deduct balance before processing
    request.user.deduct_balance(
        amount=agent.price,
        description=f"Used {agent.name} agent"
    )
    
    # Process agent request...
```

### Transaction History Page
Create `templates/wallet/history.html`:
```html
{% extends 'base.html' %}

{% block content %}
<div class="card">
    <h2>Transaction History</h2>
    <p>Current Balance: <strong>{{ current_balance }} AED</strong></p>
    
    <div class="transaction-list">
        {% for transaction in transactions %}
        <div class="transaction-item">
            <span class="amount">{{ transaction.amount }} AED</span>
            <span class="type">{{ transaction.get_type_display }}</span>
            <span class="date">{{ transaction.created_at|date:"M d, Y H:i" }}</span>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

---

## 🔧 Troubleshooting

### Common Issues:
1. **Stripe keys not working**: Verify test keys are correct in `.env`
2. **Payment not confirming**: Check browser console for JavaScript errors
3. **Balance not updating**: Ensure user model has wallet_balance field
4. **CSS not loading**: Run `python manage.py collectstatic`

### Debug Mode:
Add to views.py for debugging:
```python
import logging
logger = logging.getLogger(__name__)

# In payment views:
logger.info(f"Payment Intent created: {intent.id}")
logger.info(f"User {request.user.id} balance updated: {request.user.wallet_balance}")
```

---

## ✅ Production Checklist

Before deploying to production:
- [ ] Switch to live Stripe keys
- [ ] Set up webhook endpoints (optional but recommended)
- [ ] Enable HTTPS for secure payments
- [ ] Set DEBUG=False in settings
- [ ] Configure proper error logging
- [ ] Test with real payment amounts
- [ ] Set up monitoring for failed payments

---

This implementation provides a complete, professional wallet system with Stripe integration that works without webhooks for development and testing, while being easily extensible for production use.