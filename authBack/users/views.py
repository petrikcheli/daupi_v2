from django.shortcuts   import render
from rest_framework     import generics, status
from .serializers       import RegisterSerializer, CustomTokenSerializer
from .models            import User

from rest_framework.permissions      import IsAuthenticated
from rest_framework.views            import APIView
from rest_framework.response         import Response
from rest_framework_simplejwt.views  import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# Он уже умеет принимать запросы post проверяет email + password
# генерирует access и refresh токены а также возвращает их 
class CustomTokenView(TokenObtainPairView):     # он уже умеет принимат
    serializer_class = CustomTokenSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# Если токена нет -> 401
# Если токен битый -> 401
# Если просрочен -> 401
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "email": request.user.email,
            "username": request.user.username
        })
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token is None:
                return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # добавляем в черный список
            return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
class SearchUserView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "")

        users = User.objects.filter(username__icontains=q)

        data = [
            {
                "id": user.pk,
                "username": user.username,
            }
            for user in users
        ]

        return Response(data)