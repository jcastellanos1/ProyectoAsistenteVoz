from modules.spotify_control import SpotifyControl
from modules.commands.comunes import update_response_with_delay
from modules import db_logger

spotify = SpotifyControl()

def controlar_musica(comando):
    """Ejecuta comandos de música en Spotify."""
    try:
        if "pausa" in comando:
            db_logger.log_question("pausar spotify")
            spotify.pause_playback()
            update_response_with_delay("Música pausada")

        elif "reproducir" in comando:
            db_logger.log_question("reproducir spotify")
            spotify.start_playback()
            update_response_with_delay("Reproduciendo música")

        elif "siguiente" in comando:
            db_logger.log_question("siguiente cancion")
            spotify.next_track()
            update_response_with_delay("Siguiente canción")

        elif "anterior" in comando:
            db_logger.log_question("anterior cancion")
            spotify.previous_track()
            update_response_with_delay("Canción anterior")

        elif "qué suena" in comando or "que suena" in comando:
            db_logger.log_question("que suena")
            track_info = spotify.get_current_track()
            if track_info:
                nombre_cancion = track_info.split("]")[-1].strip()
                update_response_with_delay(nombre_cancion)
            else:
                update_response_with_delay("No se pudo obtener la información de la canción.")
    except Exception as e:
        update_response_with_delay("Hubo un problema con Spotify. Verifica que la aplicación esté abierta y que un dispositivo esté activo.")
        print(f"Error en controlar_musica: {e}")
