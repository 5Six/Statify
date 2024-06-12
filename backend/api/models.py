from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, spotify_id, spotify_display_name, spotify_email, password=None, **extra_fields):
        if not spotify_id:
            raise ValueError('The Spotify ID must be set')
        user = self.model(
            spotify_id=spotify_id,
            spotify_display_name=spotify_display_name,
            spotify_email=spotify_email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, spotify_id, spotify_display_name, spotify_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if password is None:
            raise ValueError('Superuser must have a password.')

        return self.create_user(spotify_id, spotify_display_name, spotify_email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    spotify_id = models.CharField(max_length=255, unique=True)
    spotify_display_name = models.CharField(max_length=255)
    spotify_email = models.EmailField()
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'spotify_id'
    REQUIRED_FIELDS = ['spotify_display_name', 'spotify_email']


class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.DateTimeField()
