from rest_framework         import serializers
from .models                import Friendship, FriendshipStatus
from django.contrib.auth    import get_user_model

User = get_user_model()

class SendFriendRequstSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        request_user = self.context["request"].user

        if request_user.id == value:
            raise serializers.ValidationError("Нельзя добавить себя")
        
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Пользователь не найден")
        
        return value
    
    def create(self, validated_data):
        from_user = self.context["request"].user
        to_user = User.objects.get(id=validated_data["user_id"])

        user1, user2 = sorted([from_user, to_user], key=lambda u: u.pk)

        friendship, created = Friendship.objects.get_or_create(
            user1=user1,
            user2=user2,
            defaults={"status": FriendshipStatus.PENDING}
        )

        return friendship
