from django.db import transaction
from django.db.models import Q
from .models import Friendship, FriendshipStatus

@transaction.atomic
def send_friend_request(from_user, to_user):

    if from_user == to_user:
        raise ValueError("Cannot add yourself")
    
    user1, user2 = sorted([from_user, to_user], key=lambda u: u.id)

    friendship = (
        Friendship.objects
        .select_for_update()
        .filter(user1=user1, user2=user2)
        .first()
    )

    if friendship:
        if friendship.status == FriendshipStatus.BLOCKED:
            raise ValueError("User is blocked")
        
        if friendship.status == FriendshipStatus.ACCEPTED:
            raise ValueError("Already firends")
        
        if friendship.status ==  FriendshipStatus.PENDING:
            raise ValueError("Request alreay sent")
        
        friendship.status = FriendshipStatus.PENDING
        friendship.save(update_fields=["status"])
        return friendship
    
    return Friendship.objects.create(
        user1=user1,
        user2=user2,
        status=FriendshipStatus.PENDING
    )

@transaction.atomic
def accept_friendship(friendship, user):

    if user not in [friendship.user1, friendship.user2]:
        raise PermissionError("Not allowed")
    
    if friendship.status == FriendshipStatus.BLOCKED:
        raise ValueError("Blocked users cannot be accepted")
    
    friendship.status = FriendshipStatus.ACCEPTED
    friendship.save(update_fields=["status"])

@transaction.atomic
def decline_friendship(friendship: Friendship, user):

    if user not in [friendship.user1, friendship.user2]:
        raise PermissionError("Not allowed")
    
    if friendship.status != FriendshipStatus.PENDING:
        raise ValueError("Only pending requests can be declined")
    
    friendship.status = FriendshipStatus.DECLINED
    friendship.save(update_fields=["status", "updated_at"])

    return friendship

@transaction.atomic
def block_friendship(friendship: Friendship, user):

    if user not in [friendship.user1, friendship.user2]:
        raise PermissionError("Not Allowed")
    
    if friendship.status == FriendshipStatus.BLOCKED:
        raise ValueError("Already blocked")
    
    friendship.status = FriendshipStatus.BLOCKED
    friendship.save(update_fields=["status", "updated_at"])

    return friendship