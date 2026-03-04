from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Friendship, FriendshipStatus
from .services import (
    send_friend_request,
    accept_friendship,
    decline_friendship,
    block_friendship,
)
from .serializers import SendFriendRequstSerializer

class FriendshipViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = SendFriendRequstSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        friendship = serializer.save()

        return Response({"status": friendship.status})
    
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        friendship = get_object_or_404(Friendship, pk=pk)

        accept_friendship(friendship, request.user)

        return Response({"status": "accepted"})
    

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        friendship = get_object_or_404(Friendship, pk=pk)
        decline_friendship(friendship, request.user)
        return Response({"status": "declined"})
    
    @action(detail=True, methods=["post"])
    def block(self, request, pk=None):
        friendship = get_object_or_404(Friendship, pk=pk)
        block_friendship(friendship, request.user)
        return Response({"status": "blocked"})
    
    @action(detail=False, methods=["get"])
    def incoming(self, request):
        friendships = Friendship.objects.filter(
            status=FriendshipStatus.PENDING,
            user2=request.user
        )
        return Response({"count": friendships.count()})   
    
    @action(detail=False, methods=["get"])
    def outgoing(self, request):
        friendships = Friendship.objects.filter(
            status=FriendshipStatus.PENDING,
            user1=request.user
        )
        return Response({"count": friendships.count()})
    
    @action(detail=False, methods=["get"])
    def list(self, request):
        user = request.user

        friendships = Friendship.objects.filter(
            status=FriendshipStatus.ACCEPTED
        ).filter(
            Q(user1=user) | Q(user2=user)
        ).select_related("user1", "user2")

        friends = []

        for f in friendships:
            friend = f.user2 if f.user1 == user else f.user1
            friends.append({
                "id": friend.id,
                "username": friend.username,
                "email": friend.email
            })

        return Response(friends)
    # @action(detail=False, methods=["get"])
    # def friends(self, request):
    #     user = request.user

    #     friendships = Friendship.objects.filter(
    #         status=FriendshipStatus.ACCEPTED
    #     ).filter(
    #         Q(user1=user) | Q(user2=user)
    #     ).select_related
    #     ("user1", "user2")

    #     result = []
    #     for f in friendships:
    #         friend = f.user2 if f.user1 == user else f.user1
    #         result.append({
    #             "id":       friend.id,
    #             "username": friend.username,
    #             "email":    friend.email
    #         })

    #     return Response(result)


    # @action(detail=True, methods=["post"])
    # def accept(self, request, pk=None):
    #     friendship = Friendship.objects.get(pk=pk)

    #     if request.user not in [friendship.user1, friendship.user2]:
    #         return Response(status=403)
        
    #     friendship.status = FriendshipStatus.ACCEPTED
    #     friendship.save(update_fields=["status"])

    #     return Response({"status": "accepted"})