import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from decimal import Decimal
import json
import time

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

# ✅ CRITICAL: Set API version to match webhook configuration
stripe.api_version = "2025-05-28.basil"


class StripePaymentHandler:
    def __init__(self):
        self.allowed_amounts = [10, 50, 100, 500]
    
    def create_checkout_session(self, user, amount, request=None):
        """Create a Stripe checkout session for wallet top-up (Modern Integration)"""
        if amount not in self.allowed_amounts:
            raise ValueError(f"Invalid amount: {amount}. Allowed amounts: {self.allowed_amounts}")
        
        # Build URLs with session_id parameter for payment verification
        if request:
            success_url = request.build_absolute_uri('/wallet/top-up/success/') + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri('/wallet/top-up/cancel/')
        else:
            # Fallback URLs
            success_url = 'https://netcop.up.railway.app/wallet/top-up/success/?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = 'https://netcop.up.railway.app/wallet/top-up/cancel/'
        
        try:
            print(f"🚀 [STRIPE DEBUG] Starting checkout session creation...")
            print(f"👤 User: {user.id} ({user.email})")
            print(f"💰 Amount: {amount} AED")
            print(f"🔑 Stripe API Key (last 4): ...{settings.STRIPE_SECRET_KEY[-4:]}")
            print(f"🔑 API Version: {stripe.api_version}")
            print(f"📍 Success URL: {success_url}")
            print(f"📍 Cancel URL: {cancel_url}")
            print(f"📍 Expected Webhook URL: https://netcop.up.railway.app/stripe/webhook/")
            print(f"🌍 Environment: {'production' if 'railway.app' in (request.get_host() if request else '') else 'development'}")
            
            # Create session with modern Stripe practices
            session = stripe.checkout.Session.create(
                # Modern payment method configuration
                payment_method_types=['card'],
                
                # Line items configuration
                line_items=[{
                    'price_data': {
                        'currency': 'aed',
                        'product_data': {
                            'name': 'NetCop Wallet Top-up',
                            'description': f'Add {amount} AED to your wallet balance',
                            'metadata': {
                                'service': 'netcop_wallet',
                                'user_id': str(user.id)
                            }
                        },
                        'unit_amount': int(amount * 100),  # Convert to fils (AED cents)
                    },
                    'quantity': 1,
                }],
                
                # Payment configuration
                mode='payment',
                
                # URLs with session ID parameter
                success_url=success_url,
                cancel_url=cancel_url,
                
                # Customer and reference data
                client_reference_id=str(user.id),
                customer_email=user.email,
                
                # Comprehensive metadata for webhook processing
                metadata={
                    'user_id': str(user.id),
                    'user_email': user.email,
                    'amount': str(amount),
                    'currency': 'aed',
                    'type': 'wallet_topup',
                    'service': 'netcop',
                    'environment': 'production' if 'railway.app' in (request.get_host() if request else '') else 'development',
                    'created_at': str(int(time.time())),
                    'app_version': '1.0'
                },
                
                # Modern Stripe features
                payment_intent_data={
                    'metadata': {
                        'user_id': str(user.id),
                        'amount': str(amount),
                        'service': 'netcop_wallet'
                    }
                },
                
                # Automatic tax and billing
                automatic_tax={'enabled': False},
                
                # Expiration
                expires_at=int(time.time()) + (30 * 60),  # 30 minutes from now
            )
            
            print(f"✅ [STRIPE DEBUG] Session created successfully!")
            print(f"   💳 Session ID: {session.id}")
            print(f"   👤 Client Reference: {session.client_reference_id}")
            print(f"   👤 Customer Email: {session.customer_email}")
            print(f"   💰 Amount Total: {session.amount_total} fils ({session.amount_total / 100} AED)")
            print(f"   💱 Currency: {session.currency}")
            print(f"   🔗 Payment URL: {session.url}")
            print(f"   📊 Status: {session.status}")
            print(f"   💳 Payment Status: {session.payment_status}")
            print(f"   ⏰ Created: {session.created}")
            print(f"   ⏰ Expires: {session.expires_at}")
            print(f"   🏷️ Mode: {session.mode}")
            print(f"   🆔 Object Type: {session.object}")
            print(f"   📝 Metadata: {session.metadata}")
            
            # CRITICAL: Verify session was created in correct Stripe account
            print(f"🔍 [STRIPE DEBUG] Verifying session exists immediately...")
            try:
                verification_session = stripe.checkout.Session.retrieve(session.id)
                print(f"✅ [STRIPE DEBUG] Session verification successful!")
                print(f"   🔗 Retrieved Session ID: {verification_session.id}")
                print(f"   📊 Retrieved Status: {verification_session.status}")
                print(f"   👤 Retrieved Customer Email: {verification_session.customer_email}")
            except Exception as verify_error:
                print(f"❌ [STRIPE DEBUG] Session verification FAILED: {verify_error}")
                print(f"❌ This means the session was NOT created in the expected Stripe account!")
            
            return {
                'payment_url': session.url,
                'session_id': session.id,
                'amount': amount,
                'currency': 'aed',
                'expires_at': session.expires_at
            }
            
        except stripe.error.StripeError as e:
            print(f"❌ [MODERN] Stripe error: {str(e)}")
            raise ValueError(f"Failed to create checkout session: {str(e)}")
    
    def verify_payment(self, session_id):
        """Verify payment directly from Stripe (bypasses webhook issues)"""
        try:
            print(f"🔍 [STRIPE DEBUG] Starting payment verification...")
            print(f"🔑 Using Stripe API Key (last 4): ...{settings.STRIPE_SECRET_KEY[-4:]}")
            print(f"🔑 API Version: {stripe.api_version}")
            print(f"💳 Session ID to verify: {session_id}")
            
            session = stripe.checkout.Session.retrieve(session_id)
            
            print(f"✅ [STRIPE DEBUG] Session retrieved successfully!")
            print(f"   💳 Session ID: {session.id}")
            print(f"   📊 Session Status: {session.status}")
            print(f"   💳 Payment Status: {session.payment_status}")
            print(f"   👤 Client Reference ID: {session.client_reference_id}")
            print(f"   👤 Customer Email: {session.customer_email}")
            print(f"   💰 Amount Total: {session.amount_total} fils ({session.amount_total / 100} AED)")
            print(f"   💱 Currency: {session.currency}")
            print(f"   ⏰ Created: {session.created}")
            print(f"   ⏰ Expires At: {session.expires_at}")
            print(f"   🏷️ Mode: {session.mode}")
            print(f"   📝 Metadata: {session.metadata}")
            print(f"   💳 Payment Intent: {getattr(session, 'payment_intent', 'None')}")
            print(f"   🧾 Invoice: {getattr(session, 'invoice', 'None')}")
            print(f"   🎯 Success URL: {getattr(session, 'success_url', 'None')}")
            
            # Check if payment was actually completed
            if hasattr(session, 'payment_intent') and session.payment_intent:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    print(f"💳 [STRIPE DEBUG] Payment Intent Details:")
                    print(f"   🆔 Payment Intent ID: {payment_intent.id}")
                    print(f"   📊 Status: {payment_intent.status}")
                    print(f"   💰 Amount: {payment_intent.amount} fils ({payment_intent.amount / 100} AED)")
                    print(f"   💱 Currency: {payment_intent.currency}")
                    print(f"   ⏰ Created: {payment_intent.created}")
                    print(f"   📝 Description: {payment_intent.description}")
                except Exception as pi_error:
                    print(f"❌ [STRIPE DEBUG] Could not retrieve Payment Intent: {pi_error}")
            
            if session.payment_status == 'paid' and session.status == 'complete':
                user_id = session.client_reference_id
                amount = session.amount_total / 100  # Convert from cents
                
                print(f"✅ VERIFY: Payment successful - User: {user_id}, Amount: {amount}")
                
                # Process the payment manually (bypass webhook)
                if user_id:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user = User.objects.get(id=user_id)
                        
                        # Check if already processed to avoid double-charging
                        from wallet.models import WalletTransaction
                        existing = WalletTransaction.objects.filter(stripe_session_id=session_id).first()
                        
                        if not existing:
                            print(f"💰 VERIFY: Processing payment for {user.email}")
                            user.add_balance(
                                amount=amount,
                                description=f"Wallet top-up via Stripe (Manual Verification)",
                                stripe_session_id=session_id
                            )
                            print(f"✅ VERIFY: Balance updated successfully")
                            return {
                                'success': True,
                                'amount': amount,
                                'user_id': user_id,
                                'processed': True,
                                'message': 'Payment processed via manual verification'
                            }
                        else:
                            print(f"⚠️ VERIFY: Payment already processed")
                            return {
                                'success': True,
                                'amount': amount,
                                'user_id': user_id,
                                'processed': False,
                                'message': 'Payment already processed'
                            }
                            
                    except Exception as e:
                        print(f"❌ VERIFY: Error processing payment: {e}")
                        return {'success': False, 'error': f'Processing error: {e}'}
                else:
                    return {'success': False, 'error': 'No user ID in session'}
                    
            elif session.payment_status == 'unpaid':
                return {'success': False, 'error': 'Payment not completed yet'}
            else:
                return {'success': False, 'error': f'Payment status: {session.payment_status}'}
                
        except stripe.error.StripeError as e:
            print(f"❌ VERIFY: Stripe error: {e}")
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
            print(f"📋 Session data: client_reference_id={session.get('client_reference_id')}")
            print(f"📋 Session metadata: {session.get('metadata', {})}")
            
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