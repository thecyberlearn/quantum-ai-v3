from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal


class User(AbstractUser):
    email = models.EmailField(unique=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
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
            WalletTransaction.objects.create(
                user=self,
                amount=-Decimal(str(amount)),
                type='agent_usage',
                description=description,
                agent_slug=agent_slug
            )
            return True
        return False
    
    def add_balance(self, amount, description="", stripe_session_id=""):
        self.wallet_balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        from wallet.models import WalletTransaction
        WalletTransaction.objects.create(
            user=self,
            amount=Decimal(str(amount)),
            type='top_up',
            description=description,
            stripe_session_id=stripe_session_id
        )
