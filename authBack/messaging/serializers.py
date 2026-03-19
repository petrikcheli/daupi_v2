from rest_framework import serializers
from .models import Conversation, Message, ConversationParticipant
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):

    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "type",
            "text",
            "created_at"
        ]
        read_only_fields = ["id", "sender", "created_at"]

class SendMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            "conversation",
            "type",
            "text"
        ]

    def create(self, validated_data):
        
        user = self.context["request"].user

        return Message.objects.create(
            sender=user,
            **validated_data
        )
    

class ConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = ["id", "type", "created_at"]

class CreateConversationSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField()

    class Meta:
        model = Conversation
        fields = ["user_id"]

    def create(self, validated_data):
        user = self.context["request"].user
        
        other_user = User.objects.get(id=validated_data["user_id"])

        conversation = Conversation.objects.create(type="direct")

        ConversationParticipant.objects.bulk_create([
            ConversationParticipant(conversation=conversation, user=user),
            ConversationParticipant(conversation=conversation, user=other_user),
        ])

        return conversation
    
