from django.test import TestCase

from rest_framework.test import APITestCase
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
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            self.friendship_list_url,
            {"user_id": self.user2.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Friendship.objects.count(), 1)
        self.assertEqual(Friendship.objects.first().status, FriendshipStatus.PENDING)

    # -----------------------------
    # Принять запрос
    # -----------------------------
    def test_accept_friend_request(self):
        friendship = Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse("friendship-accept", args=[friendship.id])
        response = self.client.post(url)

        friendship.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.status, FriendshipStatus.ACCEPTED)

    # -----------------------------
    # Отклонить запрос
    # -----------------------------
    def test_decline_friend_request(self):
        friendship = Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse("friendship-decline", args=[friendship.id])
        response = self.client.post(url)

        friendship.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.status, FriendshipStatus.DECLINED)

    # -----------------------------
    # Заблокировать пользователя
    # -----------------------------
    def test_block_user(self):
        friendship = Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user1)

        url = reverse("friendship-block", args=[friendship.id])
        response = self.client.post(url)

        friendship.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friendship.status, FriendshipStatus.BLOCKED)
        
    # -----------------------------
    # Входящие запросы
    # -----------------------------
    def test_incoming_requests(self):
        Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse("friendship-incoming")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    # -----------------------------
    # Исходящие запросы
    # -----------------------------
    def test_outgoing_requests(self):
        Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.PENDING
        )
        self.client.force_authenticate(user=self.user1)

        url = reverse("friendship-outgoing")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    # -----------------------------
    # Список друзей
    # -----------------------------
    def test_list_friends(self):
        Friendship.objects.create(
            user1=self.user1, user2=self.user2, status=FriendshipStatus.ACCEPTED
        )
        self.client.force_authenticate(user=self.user1)

        url = reverse("friendship-list-friends")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # -----------------------------
    # Поиск пользователей
    # -----------------------------
    def test_search_users(self):
        self.client.force_authenticate(user=self.user1)

        url = f"{self.search_url}?q=user2"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "user2")