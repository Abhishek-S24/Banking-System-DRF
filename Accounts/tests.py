from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import BankAccount
import uuid

User = get_user_model()

class AccountsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.client.force_authenticate(user=self.user)

    def test_create_bank_account(self):
        url = "/api/accounts/create/"
        data = {"account_type": "SAVINGS"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["account_type"], "SAVINGS")

    def test_list_bank_accounts(self):
        # Ensure unique account numbers
        BankAccount.objects.create(user=self.user, account_type="SAVINGS", account_number=str(uuid.uuid4()))
        url = "/api/accounts/list/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
