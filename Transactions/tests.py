from django.test import TestCase
from django.contrib.auth import get_user_model
from Accounts.models import BankAccount
from Transactions.models import Transaction

import random

User = get_user_model()

def generate_unique_account_number():
    while True:
        acc_number = str(random.randint(1000000000, 9999999999))  # 10-digit
        if not BankAccount.objects.filter(account_number=acc_number).exists():
            return acc_number

class TransactionsTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password123")

        # Create bank accounts with unique account numbers
        self.account1 = BankAccount.objects.create(
            user=self.user,
            account_type="SAVINGS",
            balance=1000,
            account_number=generate_unique_account_number()
        )
        self.account2 = BankAccount.objects.create(
            user=self.user,
            account_type="CHECKING",
            balance=500,
            account_number=generate_unique_account_number()
        )

    def test_deposit(self):
        deposit_amount = 200
        self.account1.balance += deposit_amount
        self.account1.save()
        self.assertEqual(self.account1.balance, 1200)

    def test_withdraw_success(self):
        withdraw_amount = 300
        self.account1.balance -= withdraw_amount
        self.account1.save()
        self.assertEqual(self.account1.balance, 700)

    def test_transfer_success(self):
        transfer_amount = 400
        # Deduct from account1 and add to account2
        self.account1.balance -= transfer_amount
        self.account2.balance += transfer_amount
        self.account1.save()
        self.account2.save()
        self.assertEqual(self.account1.balance, 600)
        self.assertEqual(self.account2.balance, 900)

    def test_transaction_history(self):
        # Create some transactions
        Transaction.objects.create(account=self.account1, amount=100, transaction_type="DEPOSIT")
        Transaction.objects.create(account=self.account1, amount=50, transaction_type="WITHDRAW")
        history = Transaction.objects.filter(account=self.account1)
        self.assertEqual(history.count(), 2)
