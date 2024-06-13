import base64
import requests
from datetime import timedelta
from django.utils import timezone
from .models import SpotifyToken
from statify.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


def refresh_spotify_token(user):
    spotify_token = SpotifyToken.objects.get(user=user)
    refresh_token = spotify_token.refresh_token
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()}',
    }
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    r = requests.post(url, headers=headers, data=payload)
    refresh_response_data = r.json()
    access_token = refresh_response_data.get('access_token')
    expires_in = refresh_response_data.get('expires_in')

    expires_at = timezone.now() + timedelta(seconds=expires_in)

    SpotifyToken.objects.filter(user=user).update(
        access_token=access_token,
        expires_in=expires_at,
    )

    return access_token
