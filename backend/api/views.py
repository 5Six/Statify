import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


SPOTIFY_CLIENT_ID = '2375706fa464459880921748e3178908'
SPOTIFY_CLIENT_SECRET = 'fc837fd375a44dcda9d66828b8648e71'
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/api/callback/'


# Create your views here.
@api_view(['GET'])
def login(request):
    scopes = 'user-top-read'
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
    token = request.GET.get('token')
    print(token)
    url = f'https://api.spotify.com/v1/me/top/tracks?limit=50'
    headers = {
        'Authorization': f'Bearer {token}'
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

    response = redirect('http://localhost:5173/Statify')
    response.set_cookie('spotify_token', access_token, httponly=False, secure=True)
    return response
