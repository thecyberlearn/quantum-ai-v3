from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
import uuid
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    email = models.EmailField(unique=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'wallet_balance']),
            models.Index(fields=['created_at', 'wallet_balance']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def has_sufficient_balance(self, amount):
        return self.wallet_balance >= Decimal(str(amount))
    
    def deduct_balance(self, amount, description="", agent_slug=""):
        if self.has_sufficient_balance(amount):
            self.wallet_balance -= Decimal(str(amount))
            self.save()
            
            # Create transaction record
            from wallet.models import WalletTransaction
            transaction_data = {
                'user': self,
                'amount': -Decimal(str(amount)),
                'type': 'agent_usage',
                'description': description,
                'agent_slug': agent_slug
            }
            
            # Handle stripe_payment_intent_id field if it exists (for agent usage, it's empty/null)
            try:
                WalletTransaction.objects.create(**transaction_data)
            except Exception as e:
                # If there's a NOT NULL constraint for stripe_payment_intent_id, provide empty string
                if "NOT NULL constraint failed" in str(e) and "stripe_payment_intent_id" in str(e):
                    transaction_data['stripe_payment_intent_id'] = ""
                    WalletTransaction.objects.create(**transaction_data)
                else:
                    raise e
            return True
        return False
    
    def add_balance(self, amount, description="", stripe_session_id=""):
        self.wallet_balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        from wallet.models import WalletTransaction
        transaction_data = {
            'user': self,
            'amount': Decimal(str(amount)),
            'type': 'top_up',
            'description': description,
            'stripe_session_id': stripe_session_id
        }
        
        # Handle stripe_payment_intent_id field if it exists (for wallet top-up, it's empty/null)
        try:
            WalletTransaction.objects.create(**transaction_data)
        except Exception as e:
            # If there's a NOT NULL constraint for stripe_payment_intent_id, provide empty string
            if "NOT NULL constraint failed" in str(e) and "stripe_payment_intent_id" in str(e):
                transaction_data['stripe_payment_intent_id'] = ""
                WalletTransaction.objects.create(**transaction_data)
            else:
                raise e


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        self.is_used = True
        self.save()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # 24-hour expiration for email verification
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        self.is_used = True
        self.save()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email verification token for {self.user.email}"
