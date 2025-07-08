import stripe
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeHandler:
    """Handle all Stripe-related operations"""
    
    def __init__(self):
        self.packages = {
            'basic': {'amount': 999, 'currency': 'aed', 'name': 'Basic Package - 10 AED', 'wallet_amount': 10},
            'popular': {'amount': 4999, 'currency': 'aed', 'name': 'Popular Package - 50 AED', 'wallet_amount': 50},
            'premium': {'amount': 9999, 'currency': 'aed', 'name': 'Premium Package - 100 AED', 'wallet_amount': 100},
            'enterprise': {'amount': 49999, 'currency': 'aed', 'name': 'Enterprise Package - 500 AED', 'wallet_amount': 500},
        }
    
    def create_checkout_session(self, amount, user_id, package_id):
        """Create Stripe checkout session"""
        package = self.packages.get(package_id)
        if not package:
            raise ValueError('Invalid package')
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': package['currency'],
                    'product_data': {
                        'name': package['name'],
                    },
                    'unit_amount': package['amount'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yoursite.com/wallet/success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yoursite.com/wallet/cancel/',
            client_reference_id=str(user_id),
            metadata={
                'package_id': package_id,
                'user_id': str(user_id),
            }
        )
        
        return session
    
    def handle_webhook_event(self, event):
        """Handle Stripe webhook events"""
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Get user and package info
            user_id = session['client_reference_id']
            package_id = session['metadata']['package_id']
            
            try:
                user = User.objects.get(id=user_id)
                package = self.packages.get(package_id)
                
                if package:
                    amount = package['wallet_amount']
                    user.add_balance(
                        amount,
                        f"Wallet top-up: {amount} AED",
                        session['id']
                    )
                    
            except User.DoesNotExist:
                pass

