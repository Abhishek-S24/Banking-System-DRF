from django.db import models
from django.utils import timezone

from Auth.models import User
class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings'),
        ('CURRENT', 'Current'),
    ]
    CURRENCIES = [
        ('INR', 'INR'),
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=12, unique=True  , primary_key=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='SAVINGS')
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='INR')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_number} ({self.user.username})"