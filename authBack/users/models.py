from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):

    ...
    # Переопределяем ManyToMany поля, чтобы убрать конфликты reverse accessor
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True
    )

    # Идентификация
    email = models.EmailField(unique=True, db_index=True)
    
    username = models.CharField(max_length=40, unique=True, db_index=True)

    # Персональные данные
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    #Профиль
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    status = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    #Системные поля
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(null=True, blank=True)

    #Email верификаця на будущее
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


# Create your models here.
