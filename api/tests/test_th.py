
import logging
from django.test import TestCase
from rest_framework.test import APIClient

from api.tests.utils import create_test_user

logger = logging.getLogger(__name__)

class UserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=None)
        self.admin = create_test_user(is_admin=True)
        self.user1 = create_test_user(public_sharing=True)
        self.user2 = create_test_user()

        
    # def test_user_update_own_password(self):
    #     # Log in as user1 and change password
    #     self.client.force_authenticate(user=self.user1)
    #     response = self.client.patch(
    #         f"/api/user/{self.user1.id}/", data={"password": "newpassword"}
    #     )
    #     self.assertEqual(200, response.status_code)

    #     # Log in as user1 with new password
    #     login_payload = {
    #         "username": self.user1.username,
    #         "password": "newpassword",
    #     }
    #     response = self.client.post("/api/auth/token/obtain/", data=login_payload)
    #     self.assertEqual(200, response.status_code)
    #     data = response.json()
    #     self.assertTrue("access" in data.keys())
    #     self.assertTrue("refresh" in data.keys())


    def test_admin_update_user_password(self):
        # Log in as admin and change password of user1
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/user/{self.user1.id}/", data={"password": "newpassword"}
        )
        self.assertEqual(200, response.status_code)

        # Log in as user1, given the new password of the admin
        login_payload = {
            "username": self.user1.username,
            "password": "newpassword",
        }
        response = self.client.post("/api/auth/token/obtain/", data=login_payload)
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertTrue("access" in data.keys())
        self.assertTrue("refresh" in data.keys())

    
    def test_enumeration_api(self):
        existing_users = []
        for i in range(0, 100):
            response = self.client.get(f"/api/user/{i}/")
            if response.status_code == 200:
                existing_users.append(i)
        self.assertTrue(len(existing_users) > 0)
