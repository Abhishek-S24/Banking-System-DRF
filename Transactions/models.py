from django.db import models
from django.utils import timezone


from Accounts.models import BankAccount
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('TRANSFER', 'Transfer'),
    ]

    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    reference_account = models.ForeignKey(
        BankAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='related_transactions'
    )

    def __str__(self):
        if self.transaction_type == 'TRANSFER' and self.reference_account:
            return f"{self.transaction_type}: {self.amount} from {self.account.account_number} to {self.reference_account.account_number}"
        return f"{self.transaction_type}: {self.amount} ({self.account.account_number})"