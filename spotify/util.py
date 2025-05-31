from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get
import logging

logger = logging.getLogger(__name__)
BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(session_id):
    try:
        return SpotifyToken.objects.get(user=session_id)
    except SpotifyToken.DoesNotExist:
        logger.warning(f"No Spotify tokens found for session {session_id}")
        return None


def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
                                 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(user=session_id, access_token=access_token,
                            refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()


def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        if tokens.expires_in <= timezone.now():
            refresh_spotify_token(session_id)
        return True
    return False


def refresh_spotify_token(session_id):
    tokens = get_user_tokens(session_id)
    if not tokens:
        logger.error(f"Attempted to refresh token for session {session_id} but no tokens found")
        return False

    try:
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': tokens.refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }).json()

        if 'error' in response:
            logger.error(f"Error refreshing token: {response['error']}")
            return False

        update_or_create_user_tokens(
            session_id, 
            response.get('access_token'), 
            response.get('token_type', 'Bearer'), 
            response.get('expires_in', 3600),  # Default 1 hour if not provided
            tokens.refresh_token  # Refresh token remains the same
        )
        return True
    except Exception as e:
        logger.error(f"Exception refreshing token: {str(e)}")
        return False


def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_id)
    if not tokens:
        logger.error(f"No tokens found for session {session_id}")
        return {'error': 'User not authenticated with Spotify'}

    # Refresh token if expired
    if tokens.expires_in <= timezone.now():
        if not refresh_spotify_token(session_id):
            return {'error': 'Could not refresh Spotify token'}

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {tokens.access_token}"
    }

    try:
        if post_:
            response = post(BASE_URL + endpoint, headers=headers)
        elif put_:
            response = put(BASE_URL + endpoint, headers=headers)
        else:
            response = get(BASE_URL + endpoint, headers=headers)
        
        response.raise_for_status()  # Raises exception for 4XX/5XX responses
        return response.json()
    except Exception as e:
        logger.error(f"Spotify API request failed: {str(e)}")
        return {'error': str(e)}


def play_song(session_id):
    return execute_spotify_api_request(session_id, "player/play", put_=True)


def pause_song(session_id):
    return execute_spotify_api_request(session_id, "player/pause", put_=True)


def skip_song(session_id):
    return execute_spotify_api_request(session_id, "player/next", post_=True)
