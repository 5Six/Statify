from django.contrib import admin
from .models import User, SpotifyToken

# Register your models here.

admin.site.register(SpotifyToken)
admin.site.register(User)
