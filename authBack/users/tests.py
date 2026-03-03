from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class RegisterTestCase(APITestCase):

    #---------------------------------------
    #======ТЕСТ РЕГИСТРАЦИИ======
    #---------------------------------------
    def test_user_registration(self):
        url = reverse("users:register")

        data = {
            "email": "test@mail.com",
            "username": "testuser",
            "password": "12345678"
        }

        response = self.client.post(url, data, format="json")

        # Проверяем статус
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем что пользователь создался
        self.assertTrue(User.objects.filter(email="test@mail.com").exists())

    #---------------------------------------
    #======ТЕСТ НА ПОВТОРЯЮЩИЙСЯ EMAIL======
    #---------------------------------------
    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="123456"
        )

        url = reverse("users:register")

        data = {
            "email": "test@mail.com",
            "username": "another",
            "password": "123456"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    #---------------------------------------
    #======ТЕСТ ЛОГИН======
    #---------------------------------------
    def test_login(self):
        User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="12345678"
        )

        url = reverse("users:login")

        data = {
            "email": "test@mail.com",
            "password": "12345678"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    #---------------------------------------
    #======Тест защищённого эндпоинта======
    #---------------------------------------
    def test_profile_access(self):
        user = User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="12345678"
        )

        login_url = reverse("users:login")
        response = self.client.post(login_url, {
            "email": "test@mail.com",
            "password": "12345678"
        }, format="json")

        token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        profile_url = reverse("users:profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@mail.com")

    #---------------------------------------
    #======Тест blacklist======
    #---------------------------------------
    def test_logout(self):
        user = User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="12345678"
        )

        # Логин
        login_url = reverse("users:login")
        response = self.client.post(login_url, {
            "email": "test@mail.com",
            "password": "12345678"
        }, format="json")

        refresh = response.data["refresh"]
        access = response.data["access"]

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_url = reverse("users:logout")
        response = self.client.post(logout_url, {"refresh": refresh}, format="json")

        self.assertEqual(response.status_code, 205)
    



