import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from decimal import Decimal
import json

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentHandler:
    def __init__(self):
        self.allowed_amounts = [10, 50, 100, 500]
    
    def create_checkout_session(self, user, amount, request=None):
        """Create a Stripe checkout session for wallet top-up"""
        if amount not in self.allowed_amounts:
            raise ValueError(f"Invalid amount: {amount}. Allowed amounts: {self.allowed_amounts}")
        
        # Build URLs based on current request domain
        if request:
            success_url = request.build_absolute_uri('/wallet/top-up/success/')
            cancel_url = request.build_absolute_uri('/wallet/top-up/cancel/')
        else:
            # Fallback URLs (shouldn't happen in normal flow)
            success_url = 'https://netcop.up.railway.app/wallet/top-up/success/'
            cancel_url = 'https://netcop.up.railway.app/wallet/top-up/cancel/'
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'aed',
                        'product_data': {
                            'name': f'NetCop Wallet Top-up',
                            'description': f'Add {amount} AED to your wallet balance'
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user.id),
                customer_email=user.email,
                metadata={
                    'user_id': str(user.id),
                    'amount': str(amount),
                    'type': 'wallet_topup'
                }
            )
            
            return {
                'payment_url': session.url,
                'session_id': session.id
            }
            
        except stripe.error.StripeError as e:
            raise ValueError(f"Failed to create checkout session: {str(e)}")
    
    def verify_payment(self, session_id):
        """Verify payment from Stripe webhook"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                return {
                    'success': True,
                    'amount': session.amount_total / 100,  # Convert from cents
                    'customer_email': session.customer_details.email,
                    'client_reference_id': session.client_reference_id
                }
            else:
                return {'success': False, 'error': 'Payment not completed'}
                
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}
    
    def handle_webhook(self, payload, signature):
        """Handle Stripe webhook events"""
        print(f"🔍 Processing webhook with signature: {bool(signature)}")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            print(f"📋 Event type: {event['type']}")
        except ValueError as e:
            print(f"❌ Invalid payload: {e}")
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            print(f"❌ Invalid signature: {e}")
            return {'success': False, 'error': 'Invalid signature'}
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(f"💳 Processing checkout session: {session['id']}")
            
            # Process successful payment
            user_id = session.get('client_reference_id')
            amount = session['amount_total'] / 100  # Convert from cents
            
            print(f"👤 User ID: {user_id}, Amount: {amount} AED")
            
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    print(f"✅ Found user: {user.email}, Current balance: {user.wallet_balance}")
                    
                    user.add_balance(
                        amount=amount,
                        description=f"Wallet top-up via Stripe",
                        stripe_session_id=session['id']
                    )
                    user.refresh_from_db()
                    print(f"💰 New balance: {user.wallet_balance}")
                    
                    return {'success': True, 'message': 'Payment processed successfully'}
                except User.DoesNotExist:
                    print(f"❌ User not found: {user_id}")
                    return {'success': False, 'error': 'User not found'}
            else:
                print("❌ No user_id in session")
                return {'success': False, 'error': 'No user reference'}
        else:
            print(f"ℹ️ Ignored event type: {event['type']}")
        
        return {'success': True, 'message': 'Event processed'}
    
    def process_refund(self, session_id, amount=None):
        """Process refund for a payment"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment_intent = session.payment_intent
            
            if amount:
                refund = stripe.Refund.create(
                    payment_intent=payment_intent,
                    amount=int(amount * 100)  # Convert to cents
                )
            else:
                refund = stripe.Refund.create(payment_intent=payment_intent)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status
            }
            
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}