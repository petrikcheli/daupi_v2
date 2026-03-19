from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from messaging.models import Conversation, Message, ConversationParticipant

User = get_user_model()


class ChatAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            email="user1@test.com", username="user1", password="12345678"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com", username="user2", password="12345678"
        )

        self.client.force_authenticate(user=self.user1)

        self.conversation_url = reverse("conversation-list")
        self.message_url = reverse("message-list")
        self.history_url = reverse("message-history")
        self.read_url = reverse("message-read")

    # -----------------------------
    # Создание диалога
    # -----------------------------
    def test_create_conversation(self):
        response = self.client.post(
            self.conversation_url,
            {"user_id": self.user2.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(ConversationParticipant.objects.count(), 2)

    # -----------------------------
    # Получение списка диалогов
    # -----------------------------
    def test_list_conversations(self):
        conv = Conversation.objects.create(type="direct")

        ConversationParticipant.objects.create(
            conversation=conv, user=self.user1
        )
        ConversationParticipant.objects.create(
            conversation=conv, user=self.user2
        )

        response = self.client.get(self.conversation_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # -----------------------------
    # Отправка сообщения
    # -----------------------------
    def test_send_message(self):
        conv = Conversation.objects.create(type="direct")

        ConversationParticipant.objects.create(
            conversation=conv, user=self.user1
        )
        ConversationParticipant.objects.create(
            conversation=conv, user=self.user2
        )

        response = self.client.post(
            self.message_url,
            {
                "conversation": conv.id,
                "type": "text",
                "text": "Hello"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().text, "Hello")

    # -----------------------------
    # История сообщений
    # -----------------------------
    def test_message_history(self):
        conv = Conversation.objects.create(type="direct")

        ConversationParticipant.objects.create(
            conversation=conv, user=self.user1
        )

        Message.objects.create(
            conversation=conv,
            sender=self.user1,
            text="Test message"
        )

        response = self.client.get(
            self.history_url,
            {"conversation_id": conv.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # -----------------------------
    # Отметить сообщение как прочитанное
    # -----------------------------
    def test_mark_as_read(self):
        conv = Conversation.objects.create(type="direct")

        participant = ConversationParticipant.objects.create(
            conversation=conv,
            user=self.user1
        )

        msg = Message.objects.create(
            conversation=conv,
            sender=self.user1,
            text="Hello"
        )

        response = self.client.post(
            self.read_url,
            {
                "conversation_id": conv.id,
                "message_id": msg.id
            },
            format="json"
        )

        participant.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(participant.last_read_message, msg)