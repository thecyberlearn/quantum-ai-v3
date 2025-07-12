# Payment System Documentation

## Overview

NetCop Hub uses a Stripe-based payment system with API verification for reliable, instant wallet top-ups. The system bypasses webhook dependencies by verifying payments directly with the Stripe API when users return from successful payments.

## Architecture

### API-Based Verification (Current Implementation)

Instead of relying on webhooks, the system uses direct API calls for payment verification:

```
User Payment Flow:
1. User selects amount → Stripe checkout session created
2. User pays on Stripe → Returns to success page with session_id
3. Success page calls Stripe API → Verifies payment status
4. If paid → Wallet balance updated immediately
5. User sees instant confirmation
```

## Setup Guide

### 1. Stripe Account Setup

1. **Create Stripe Account**: https://dashboard.stripe.com/register
2. **Get API Keys**:
   - Go to Dashboard → Developers → API keys
   - Copy **Publishable key** (starts with `pk_test_`)
   - Copy **Secret key** (starts with `sk_test_`)

### 2. Environment Configuration

Add to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here  # Optional
```

### 3. Django Settings

The settings are automatically configured in `settings.py`:

```python
# Stripe Configuration (automatically loaded from .env)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
```

### 4. Railway Deployment

Add environment variables in Railway dashboard:

1. Go to your Railway project
2. Navigate to Variables tab
3. Add:
   - `STRIPE_SECRET_KEY` = `sk_test_...`
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` = `pk_test_...`
   - `STRIPE_WEBHOOK_SECRET` = `whsec_...` (optional)

## Payment Flow Details

### 1. Checkout Session Creation

**File**: `wallet/stripe_handler.py`

```python
def create_checkout_session(self, user, amount, request=None):
    # Creates Stripe checkout session
    # Includes user metadata and success URL with session_id parameter
    # Returns payment URL for redirect
```

**Features**:
- Validates allowed amounts (10, 50, 100, 500 AED)
- Includes comprehensive metadata
- Auto-expires after 30 minutes
- Immediate verification after creation

### 2. Payment Verification

**File**: `core/views.py` - `wallet_topup_success_view()`

```python
def wallet_topup_success_view(request):
    session_id = request.GET.get('session_id')
    # Verify payment with Stripe API
    # Update wallet balance if successful
    # Show confirmation message
```

**Process**:
1. Extract `session_id` from URL parameters
2. Call `stripe.checkout.Session.retrieve(session_id)`
3. Check if `payment_status == 'paid'` and `status == 'complete'`
4. Update user wallet balance
5. Create transaction record
6. Redirect to wallet with success message

### 3. Error Handling

- **Missing session_id**: Shows error, redirects to wallet
- **Payment not completed**: Shows warning with instructions
- **API errors**: Graceful error handling with user-friendly messages
- **Duplicate processing**: Prevents double-charging with session ID checks

## API Endpoints

### Core Wallet URLs

- `GET /wallet/` - Wallet dashboard and transaction history
- `GET /wallet/topup/` - Payment amount selection page
- `POST /wallet/topup/` - Create Stripe checkout session
- `GET /wallet/top-up/success/?session_id=cs_...` - Payment verification
- `GET /wallet/top-up/cancel/` - Payment cancellation handling

### Debug Endpoints (Development)

- `GET /stripe/debug/` - Test Stripe API connectivity and account info
- `POST /stripe/webhook/` - Webhook endpoint (backup, not actively used)

## Database Schema

### WalletTransaction Model

```python
class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20)  # 'top_up' or 'agent_usage'
    description = models.CharField(max_length=255)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### User Wallet Methods

```python
class User(AbstractUser):
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def add_balance(self, amount, description, stripe_session_id=None):
        # Adds money to wallet and creates transaction record
    
    def deduct_balance(self, amount, description, agent_slug):
        # Removes money for agent usage
```

## Testing

### Test Payment Flow

1. **Local Testing**:
   ```bash
   python manage.py runserver
   # Visit http://localhost:8000/wallet/topup/
   # Use test card: 4242 4242 4242 4242
   ```

2. **Stripe Test Cards**:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - **Requires authentication**: `4000 0025 0000 3155`

3. **Debugging**:
   - Visit `/stripe/debug/` to test API connectivity
   - Check Railway logs for payment verification details
   - Monitor Stripe dashboard for session creation

### Test Scenarios

- ✅ **Successful payment**: Amount added, transaction recorded
- ✅ **Cancelled payment**: No charge, user returned to form
- ✅ **Duplicate session**: Prevents double-charging
- ✅ **Network errors**: Graceful error handling
- ✅ **Invalid session**: Error message with support contact

## Troubleshooting

### Common Issues

1. **"No session found"**:
   - Check if session_id parameter is in success URL
   - Verify Stripe API keys are correct
   - Check Railway environment variables

2. **"Payment verification failed"**:
   - Confirm payment was completed on Stripe
   - Check Stripe dashboard for payment status
   - Verify API version compatibility

3. **"Session already processed"**:
   - Normal behavior - prevents double-charging
   - User balance was already updated

### Debug Steps

1. **Check Stripe Configuration**:
   ```bash
   # Visit debug endpoint
   curl https://your-app.up.railway.app/stripe/debug/
   ```

2. **Verify Environment Variables**:
   ```bash
   # In Railway dashboard, check Variables tab
   # Ensure all Stripe keys are set correctly
   ```

3. **Monitor Logs**:
   ```bash
   # Railway logs show detailed payment verification
   # Look for "[STRIPE DEBUG]" messages
   ```

## Security Considerations

### API Key Security
- ✅ **Secret keys**: Stored in environment variables, never in code
- ✅ **Publishable keys**: Safe to expose in frontend
- ✅ **Test vs Live**: Always use test keys for development

### Payment Security
- ✅ **Amount validation**: Only allows predefined amounts (10, 50, 100, 500)
- ✅ **User authentication**: All payment endpoints require login
- ✅ **Session verification**: Direct API verification prevents tampering
- ✅ **Duplicate prevention**: Session ID tracking prevents double-charging

### Data Protection
- ✅ **No sensitive data storage**: Credit card info handled by Stripe
- ✅ **Transaction records**: Only store metadata and amounts
- ✅ **User privacy**: Email and user ID properly associated

## Advantages of This Approach

### vs Webhooks
- **Reliability**: No webhook delivery failures
- **Speed**: Instant verification when user returns
- **Debugging**: Easier to trace and debug payment flows
- **User Experience**: Immediate feedback and balance updates

### vs Frontend-Only
- **Security**: Server-side verification prevents tampering
- **Reliability**: Works even if frontend JavaScript fails
- **Data Integrity**: Database updates happen server-side

### Production Ready
- **Scalability**: API calls scale better than webhook processing
- **Monitoring**: Easier to monitor and alert on payment issues
- **Maintenance**: Simpler codebase without webhook infrastructure

## Migration from Webhook System

If migrating from a webhook-based system:

1. **Remove webhook endpoints** and processing code
2. **Update success URLs** to include `{CHECKOUT_SESSION_ID}` parameter
3. **Implement verification** in success page handler
4. **Test thoroughly** with test payments
5. **Monitor logs** during transition period

The API-based approach is more reliable and provides better user experience than webhook-dependent systems.