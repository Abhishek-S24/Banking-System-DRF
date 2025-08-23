from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class RolesPermissionsTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_role(self):
        url = "/api/roles/roles/"
        data = {"name": "Manager" , "permission" : []}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_roles(self):
        url = "/api/roles/roles/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_permission(self):
        url = "/api/roles/permission/"
        data = {"code": "view_transactions"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
