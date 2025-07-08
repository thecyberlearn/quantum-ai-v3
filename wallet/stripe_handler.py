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
        self.payment_links = {
            10: 'https://buy.stripe.com/test_28EbJ16AA7ly3ic7vh2VG0a',
            50: 'https://buy.stripe.com/test_4gM00jbUUgW83ic3f12VG0b',
            100: 'https://buy.stripe.com/test_aFadR99MM35ibOI6rd2VG0c',
            500: 'https://buy.stripe.com/test_14AbJ12kk7lyf0U16T2VG0d'
        }
    
    def create_checkout_session(self, user, amount):
        """Create a Stripe checkout session for wallet top-up"""
        if amount not in self.payment_links:
            raise ValueError(f"Invalid amount: {amount}")
        
        payment_link = self.payment_links[amount]
        
        # Return the payment link URL with user reference
        return {
            'payment_url': f"{payment_link}?client_reference_id={user.id}&prefilled_email={user.email}",
            'session_id': None  # Payment links don't have session IDs
        }
    
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
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError:
            return {'success': False, 'error': 'Invalid signature'}
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Process successful payment
            user_id = session.get('client_reference_id')
            amount = session['amount_total'] / 100  # Convert from cents
            
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    user.add_balance(
                        amount=amount,
                        description=f"Wallet top-up via Stripe",
                        stripe_session_id=session['id']
                    )
                    return {'success': True, 'message': 'Payment processed successfully'}
                except User.DoesNotExist:
                    return {'success': False, 'error': 'User not found'}
        
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