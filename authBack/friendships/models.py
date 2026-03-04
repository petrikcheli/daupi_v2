from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class FriendshipStatus(models.TextChoices):
    PENDIGN  = "PENDING"  ,"Pending"
    ACCEPTED = "ACCEPTED" ,"Accepted"
    DECLINED = "DECLINED" ,"Declined"
    BLOCKED  = "BLOCKED"  ,"Blocked"

class Friendship(models.Model):
    user1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="friendships_as_user1"
    )

    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendships_as_user2"
    )

    status = models.CharField(
        max_length=10,
        choices=FriendshipStatus.choices,
        default=FriendshipStatus.PENDIGN
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)\
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_friendship_pair"
            )
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user1", "status"]),
            models.Index(fields=["user2", "status"])
        ]

    def save(self, *args, **kwargs):
        if self.user1_id > self.user2_id:
            self.user1_id, self.user2 = self.user2_id, self.user1_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user1} - {self.user2} ({self.status})"