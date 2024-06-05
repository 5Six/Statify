from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login, name='spotify-login'),
    path('logout/', logout, name='logout'),
    path('callback/', spotify_callback, name='spotify-callback'),
    path('get_most_played_song/', get_most_played_song, name='get_most_played_song')
]