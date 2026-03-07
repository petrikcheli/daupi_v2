from django.shortcuts import render

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from .models import Conversation, Message, ConversationParticipant
from .serializers import(
    ConversationSerializer,
    CreateConversationSerializer,
    MessageSerializer,
    SendMessageSerializer
)

class ConversationViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):

        conversation = Conversation.objects.filter(
            participants__user=request.user
        ).distinct()

        serializer = ConversationSerializer(conversation, many=True)

        return Response(serializer.data)
    
    @transaction.atomic
    def create(self, request):

        serializer = CreateConversationSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        conversation: Conversation = serializer.save() # type: ignore

        return Response({
            "conversation_id": conversation.pk
        })
    
class MessageViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    #Отправить сообщение
    @transaction.atomic
    def create(self, request):

        serializer = SendMessageSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        message: Message = serializer.save() # type: ignore

        return Response(MessageSerializer(message).data)
    
    # История сообщений
    @transaction.atomic
    def history(self, request):

        conversation_id = request.query_params.get("conversation_id")

        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related("sender").order_by("-id")[:50]

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    #Отметить прочитанным
    @action(detail=False, methods=["post"])
    def read(self, request):

        conversation_id = request.data.get("conversation_id")
        message_id = request.data.get("message_id")

        participant = ConversationParticipant.objects.get(
            conversation_id=conversation_id,
            user=request.user
        )

        participant.last_read_message = message_id
        participant.save(update_fields=["last_read_message"])

        return Response({"status": "ok"})
    
