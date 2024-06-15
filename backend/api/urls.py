from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login, name='spotify-login'),
    path('logout/', logout, name='logout'),
    path('callback/', spotify_callback, name='spotify-callback'),
    path('get_most_played_song/', get_most_played_song, name='get_most_played_song'),
    path('get_playlist/', get_playlist, name='get_playlist'),
    path('get_playlist_random_song/', get_playlist_random_song, name='get_playlist_random_song'),
    path('get_all_playlist_tracks/', get_all_playlist_tracks, name='get_all_playlist_tracks'),

]