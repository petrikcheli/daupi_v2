from django.test import TestCase

from rest_framework.response import Response
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from friendships.models import Friendship, FriendshipStatus

User = get_user_model()


class FriendshipAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@test.com", username="user1", password="12345678"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com", username="user2", password="12345678"
        )
        self.user3 = User.objects.create_user(
            email="user3@test.com", username="user3", password="12345678"
        )

        # Base URL
        self.friendship_list_url = reverse("friendship-list")
        self.search_url = reverse("users:search")  # /users/search/?q=

    # -----------------------------
    # Отправка запроса
    # -----------------------------
    def test_send_friend_request(self):
        self.client = APIClient()

        self.client.force_authenticate(user=self.user1)

        response: Response = self.client.post(
            self.friendship_list_url,
            {"user_id": self.user2.pk},
            format="json"
        ) # type: ignore

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Friendship.objects.count(), 1)
        self.assertEqual(Friendship.objects.first().status, FriendshipStatus.PENDING) # type: ignore

    # -----------------------------
    # Принять запрос
    # -----------------------------
    def test_accept_friend_request(self):
        self.client = APIClient()

        friendship = Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse("friendship-accept", args=[friendship.pk])
        response: Response = self.client.post(url) # type: ignore

        friendship.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.status, FriendshipStatus.ACCEPTED)

    # -----------------------------
    # Отклонить запрос
    # -----------------------------
    def test_decline_friend_request(self):
        self.client = APIClient()

        friendship = Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse("friendship-decline", args=[friendship.pk])
        response: Response = self.client.post(url) # type: ignore

        friendship.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.status, FriendshipStatus.DECLINED)

    # -----------------------------
    # Заблокировать пользователя
    # -----------------------------
    def test_block_user(self):
        self.client = APIClient()

        friendship = Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user1)

        url = reverse("friendship-block", args=[friendship.pk])
        response: Response = self.client.post(url) # type: ignore

        friendship.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.status, FriendshipStatus.BLOCKED)
        
    # -----------------------------
    # Входящие запросы
    # -----------------------------
    def test_incoming_requests(self):
        self.client = APIClient()

        Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse("friendship-incoming")
        response: Response = self.client.get(url) # type: ignore

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore


    # -----------------------------
    # Исходящие запросы
    # -----------------------------
    def test_outgoing_requests(self):
        self.client = APIClient()

        Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user1)

        url = reverse("friendship-outgoing")
        response: Response = self.client.get(url) # type: ignore

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore
    
    # -----------------------------
    # Список друзей
    # -----------------------------
    def test_list_friends(self):
        self.client = APIClient()

        Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.ACCEPTED
        )
        self.client.force_authenticate(user=self.user1)

        url = reverse("friendship-list-friends")
        response: Response = self.client.get(url) # type: ignore

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore

    # -----------------------------
    # Поиск пользователей
    # -----------------------------
    def test_search_users(self):
        self.client = APIClient()

        self.client.force_authenticate(user=self.user1)

        url = f"{self.search_url}?q=user2"
        response: Response = self.client.get(url) # type: ignore

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore
        self.assertEqual(response.data[0]["username"], "user2")# type: ignore