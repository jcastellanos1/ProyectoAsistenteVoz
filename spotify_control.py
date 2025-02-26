import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import time
import subprocess
import psutil

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

    def pause_playback(self):
        """Pausa la reproducción."""
        self.authenticate()
        if self.sp:
            self.sp.pause_playback()
            return f"[{self.user_id}]  Reproducción pausada"
        return f"[{self.user_id}]  No se pudo pausar la reproducción"

    def next_track(self):
        """Salta a la siguiente canción."""
        self.authenticate()
        if self.sp:
            self.sp.next_track()
            return f"[{self.user_id}] Siguiente canción"
        return f"[{self.user_id}]  No se pudo cambiar de canción"

    def previous_track(self):
        """Vuelve a la canción anterior."""
        self.authenticate()
        if self.sp:
            self.sp.previous_track()
            return f"[{self.user_id}] Canción anterior"
        return f"[{self.user_id}]  No se pudo regresar de canción"

    def set_volume(self, volume):
        """Ajusta el volumen (0-100)."""
        self.authenticate()
        if self.sp:
            self.sp.volume(volume)
            return f"[{self.user_id}] Volumen ajustado a {volume}%"
        return f"[{self.user_id}]  No se pudo ajustar el volumen"

    def get_current_track(self):
        """Obtiene la canción en reproducción."""
        self.authenticate()
        if self.sp:
            track = self.sp.current_playback()
            if track and track['item']:
                return f"[{self.user_id}] Reproduciendo: {track['item']['name']} - {track['item']['artists'][0]['name']}"
        return f"[{self.user_id}]  No hay música en reproducción"
    
    def is_spotify_running(self):
        """Verifica si Spotify está abierto en el sistema."""
        for process in psutil.process_iter(['name']):
            if process.info['name'] and 'Spotify' in process.info['name']:
                return True
        return False

    def get_active_device(self):
        """Obtiene el ID de un dispositivo activo en Spotify."""
        devices = self.sp.devices()
        for device in devices['devices']:
            if device['is_active']:
                return device['id']
        return None

    def get_first_available_device(self):
        """Obtiene el primer dispositivo disponible si no hay uno activo."""
        devices = self.sp.devices()
        if devices['devices']:
            return devices['devices'][0]['id']
        return None

    def start_playback(self, song_name=None):
        """Inicia la reproducción de una canción en Spotify."""
        # Verificar si Spotify está abierto en el sistema
        if not self.is_spotify_running():
            print("Spotify no está abierto. Abriéndolo...")
            os.system("start spotify.exe")  # Abre Spotify en Windows
            time.sleep(5)  # Esperar que se inicie

        # Autenticar antes de hacer cualquier acción
        self.authenticate()

        # Verificar si hay un dispositivo activo
        device_id = self.get_active_device()

        if not device_id:
            print("No hay dispositivos activos. Buscando uno disponible...")
            device_id = self.get_first_available_device()

            if not device_id:
                print("No se encontraron dispositivos disponibles. Abre Spotify en algún dispositivo y reprodúcelo manualmente una vez.")
                return
            
            # Transferir la reproducción al dispositivo disponible
            self.sp.transfer_playback(device_id, force_play=True)
            time.sleep(2)  # Esperar que la transferencia se complete

        # Si no se especificó una canción, simplemente reanuda la reproducción
        if not song_name:
            try:
                self.sp.start_playback(device_id=device_id)
                print(" Reproducción iniciada correctamente.")
            except spotipy.exceptions.SpotifyException as e:
                print(f" Error al iniciar la reproducción: {e}")
            return

        # 🔍 Buscar la canción específica
        print(f"Buscando la canción: {song_name}...")

        query = f"track:{song_name}"
        results = self.sp.search(q=query, type="track", limit=1)

        if not results['tracks']['items']:
            print("No se encontró la canción. Intenta con otro nombre.")
            return

        track = results['tracks']['items'][0]
        track_uri = track['uri']
        track_name = track['name']
        track_artist = track['artists'][0]['name']

        print(f" Reproduciendo: {track_name} de {track_artist}")

        # Reproducir la canción encontrada
        self.sp.start_playback(device_id=device_id, uris=[track_uri])
