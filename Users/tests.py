from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.client.force_authenticate(user=self.admin_user)
        self.user_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "pass123"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        url = "/api/user/register/"
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_list(self):
        url = "/api/user/users/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_get_user_detail(self):
        url = f"/api/user/users/{self.user.email}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_user_put(self):
        url = f"/api/user/users/{self.user.email}/"
        data = {"username": "updateduser", "email": self.user.email}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_partial_update_user_patch(self):
        url = f"/api/user/users/{self.user.email}/"
        data = {"username": "patcheduser"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "patcheduser")

    def test_deactivate_user(self):
        url = f"/api/user/users/{self.user.email}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.active)
