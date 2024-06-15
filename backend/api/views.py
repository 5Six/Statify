import requests
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from adrf.decorators import api_view as aapi_view
from rest_framework.authtoken.models import Token
from datetime import timedelta
import random
import math
import time
import httpx
import asyncio
from asgiref.sync import sync_to_async, async_to_sync

from .models import User, SpotifyToken
from .utils import refresh_spotify_token

from statify.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI



# Create your views here.
@api_view(['GET'])
def login(request):
    scopes = 'user-read-private user-read-email user-top-read'
    auth_url = (
        "https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={SPOTIFY_CLIENT_ID}&scope={scopes}&redirect_uri={SPOTIFY_REDIRECT_URI}&show_dialog={True}"
    )
    return redirect(auth_url)


@api_view(['POST'])
def logout(request):
    response = Response({'message': 'Logged out successfully'}, status=200)
    response.delete_cookie('spotify_token')
    return response


@api_view(['GET'])
def get_most_played_song(request):
    spotify_token = SpotifyToken.objects.get(user=request.user)
    access_token = spotify_token.access_token

    if spotify_token.expires_in < timezone.now():
        access_token = refresh_spotify_token(request.user)

    url = 'https://api.spotify.com/v1/me/top/tracks?limit=50'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    r = requests.get(url, headers=headers)

    data = r.json()

    return Response(data)


@api_view(['GET'])
def spotify_callback(request):
    code = request.GET.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_data = r.json()
    access_token = token_response_data.get('access_token')
    refresh_token = token_response_data.get('refresh_token')
    expires_in = token_response_data.get('expires_in')

    # Get user data
    user_info_url = 'https://api.spotify.com/v1/me'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info_data = user_info_response.json()

    spotify_id = user_info_data['id']
    spotify_display_name = user_info_data['display_name']
    spotify_email = user_info_data['email']

    user, created = User.objects.get_or_create(
        spotify_id=spotify_id,
        defaults={
            'spotify_display_name': spotify_display_name,
            'spotify_email': spotify_email
        }
    )

    if not created:
        user.spotify_display_name = spotify_display_name
        user.spotify_email = spotify_email
        user.save()

    expires_at = timezone.now() + timedelta(seconds=expires_in)

    SpotifyToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': expires_at,
        }
    )

    token, updated = Token.objects.update_or_create(user=user)

    response = redirect('http://localhost:5173/Statify')
    response.set_cookie('spotify_token', access_token, httponly=False, secure=True)
    response.set_cookie('auth_token', token.key, httponly=False, secure=True)

    return response

@api_view(['GET'])
def get_playlist(request):
    spotify_token = SpotifyToken.objects.get(user=request.user)
    access_token = spotify_token.access_token

    if spotify_token.expires_in < timezone.now():
        access_token = refresh_spotify_token(request.user)

    url = f'https://api.spotify.com/v1/playlists/{request.GET.get('playlist_id')}'
    header = {'Authorization': f'Bearer {access_token}'}

    r = requests.get(url, headers=header)

    data = r.json()

    return Response(data)

@api_view(['GET'])
def get_playlist_random_song(request):
    spotify_token = SpotifyToken.objects.get(user=request.user)
    access_token = spotify_token.access_token

    if spotify_token.expires_in < timezone.now():
        access_token = refresh_spotify_token(request.user)

    url = f'https://api.spotify.com/v1/playlists/{request.GET.get('playlist_id')}/tracks?&limit=1'
    header = {'Authorization': f'Bearer {access_token}'}

    r = requests.get(url, headers=header)

    data = r.json()

    tracks_total = data['total']

    n = random.randint(0, tracks_total-1)
    url = f'https://api.spotify.com/v1/playlists/{request.GET.get('playlist_id')}/tracks?offset={n}&limit=1'
    header = {'Authorization': f'Bearer {access_token}'}

    r = requests.get(url, headers=header)

    data = r.json()

    print(data['items'][0]['track']['name'])

    return Response(data)


@aapi_view(['GET'])
async def get_all_playlist_tracks(request):
    start = time.time()
    spotify_token = await sync_to_async(SpotifyToken.objects.get)(user=request.user)
    access_token = spotify_token.access_token
    if spotify_token.expires_in < timezone.now():
        access_token = refresh_spotify_token(request.user)

    url = f'https://api.spotify.com/v1/playlists/{request.GET.get('playlist_id')}/tracks?&limit=1'
    header = {'Authorization': f'Bearer {access_token}'}

    r = requests.get(url, headers=header)

    data = r.json()
    tracks_total = data['total']

    urls = []
    for i in range(math.ceil(tracks_total / 100)):
        urls.append(f'https://api.spotify.com/v1/playlists/{request.GET.get('playlist_id')}/tracks?offset={100 * i}&limit=100')

    tasks = [get_100_tracks(url, access_token) for url in urls]
    results = await asyncio.gather(*tasks)

    names = []
    for result in results:
        for item in result['items']:
            artists = []
            for artist in item['track']['artists']:
                artists.append(artist['name'])
            names.append((item['track']['name'], artists, item['track']['preview_url']))

    end = time.time()
    print(end-start)
    return Response(names)


async def get_100_tracks(url, access_token):
    async with httpx.AsyncClient() as client:
        header = {'Authorization': f'Bearer {access_token}'}
        r = await client.get(url, headers=header)
        return r.json()

@api_view(['GET'])
def search(request):
    pass