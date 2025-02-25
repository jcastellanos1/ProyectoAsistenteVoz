import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import time

load_dotenv()

class SpotifyControl:
    def __init__(self):
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        self.scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private"

        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        
        self.token_info = None
        self.sp = None
        self.last_token_refresh = 0

        self.user_id = self.get_user_id()  # 🔹 Asignar automáticamente el user_id

    def get_token(self):
        """Obtiene y refresca el token si es necesario."""
        if not self.token_info or time.time() - self.last_token_refresh > 3500:
            print("Refrescando token de Spotify...")
            self.token_info = self.sp_oauth.get_access_token(as_dict=True)
            if not self.token_info or 'access_token' not in self.token_info:
                print("Error: No se encontró un token válido.")
                return False
            self.last_token_refresh = time.time()
        return self.token_info['access_token']

    def authenticate(self):
        """Autentica y refresca el token antes de ejecutar comandos."""
        access_token = self.get_token()
        if access_token:
            self.sp = spotipy.Spotify(auth=access_token)
        else:
            print("Error de autenticación en Spotify")

    def get_user_id(self):
        """Obtiene el ID del usuario autenticado en Spotify."""
        self.authenticate()
        if self.sp:
            user_data = self.sp.current_user()
            return user_data.get("id", "default_user")  # Si falla, usa "default_user"
        return "default_user"

    def start_playback(self):
        """Reanuda la reproducción."""
        self.authenticate()
        if self.sp:
            self.sp.start_playback()
            return f"[{self.user_id}] ▶️ Reproducción iniciada"
        return f"[{self.user_id}]  No se pudo iniciar la reproducción"

    def pause_playback(self):
        """Pausa la reproducción."""
        self.authenticate()
        if self.sp:
            self.sp.pause_playback()
            return f"[{self.user_id}] ⏸️ Reproducción pausada"
        return f"[{self.user_id}]  No se pudo pausar la reproducción"

    def next_track(self):
        """Salta a la siguiente canción."""
        self.authenticate()
        if self.sp:
            self.sp.next_track()
            return f"[{self.user_id}] ⏭️ Siguiente canción"
        return f"[{self.user_id}]  No se pudo cambiar de canción"

    def previous_track(self):
        """Vuelve a la canción anterior."""
        self.authenticate()
        if self.sp:
            self.sp.previous_track()
            return f"[{self.user_id}] ⏮️ Canción anterior"
        return f"[{self.user_id}]  No se pudo regresar de canción"

    def set_volume(self, volume):
        """Ajusta el volumen (0-100)."""
        self.authenticate()
        if self.sp:
            self.sp.volume(volume)
            return f"[{self.user_id}] 🔊 Volumen ajustado a {volume}%"
        return f"[{self.user_id}]  No se pudo ajustar el volumen"

    def get_current_track(self):
        """Obtiene la canción en reproducción."""
        self.authenticate()
        if self.sp:
            track = self.sp.current_playback()
            if track and track['item']:
                return f"[{self.user_id}] 🎵 Reproduciendo: {track['item']['name']} - {track['item']['artists'][0]['name']}"
        return f"[{self.user_id}]  No hay música en reproducción"