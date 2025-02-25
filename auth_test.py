import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

os.environ["SPOTIPY_CLIENT_ID"] = "TU_CL11d789ed28754bf48a0ad49e7a3ddecdIENT_ID"
os.environ["SPOTIPY_CLIENT_SECRET"] = "332a01707a104f719c456fce7381743c"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8080/callback"

scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

user_info = sp.current_user()
print(f"Autenticado como: {user_info['display_name']} (ID: {user_info['id']})")
