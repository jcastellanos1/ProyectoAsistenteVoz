import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import time

# Cargar credenciales desde .env
load_dotenv()

class SpotifyControl:
    def __init__(self):
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        self.scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
        
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        self.token_info = None
        self.sp = None
        self.last_token_refresh = 0

    def get_token(self):
        """Obtiene y refresca el token si es necesario."""
        if not self.token_info or time.time() - self.last_token_refresh > 3500:
            print("Refrescando token de Spotify...")
            self.token_info = self.sp_oauth.get_cached_token()
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

    def start_playback(self):
        """Reanuda la reproducción."""
        self.authenticate()
        if self.sp:
            self.sp.start_playback()
            return "▶️ Reproducción iniciada"
        return " No se pudo iniciar la reproducción"

    def pause_playback(self):
        """Pausa la reproducción."""
        self.authenticate()
        if self.sp:
            self.sp.pause_playback()
            return "⏸️ Reproducción pausada"
        return " No se pudo pausar la reproducción"

    def next_track(self):
        """Salta a la siguiente canción."""
        self.authenticate()
        if self.sp:
            self.sp.next_track()
            return "⏭️ Siguiente canción"
        return " No se pudo cambiar de canción"

    def previous_track(self):
        """Vuelve a la canción anterior."""
        self.authenticate()
        if self.sp:
            self.sp.previous_track()
            return "⏮️ Canción anterior"
        return "No se pudo regresar de canción"

    def set_volume(self, volume):
        """Ajusta el volumen (0-100)."""
        self.authenticate()
        if self.sp:
            self.sp.volume(volume)
            return f"🔊 Volumen ajustado a {volume}%"
        return " No se pudo ajustar el volumen"

    def get_current_track(self):
        """Obtiene la canción en reproducción."""
        self.authenticate()
        if self.sp:
            track = self.sp.current_playback()
            if track and track['item']:
                return f"🎵 Reproduciendo: {track['item']['name']} - {track['item']['artists'][0]['name']}"
        return " No hay música en reproducción"
