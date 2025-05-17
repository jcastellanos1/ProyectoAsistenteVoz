from modules.spotify_control import SpotifyControl
from modules.commands.comunes import update_response_with_delay
from modules import db_logger

spotify = SpotifyControl()

def controlar_musica(accion):
    """Controla Spotify según una acción específica recibida como entidad del modelo."""
    try:
        match accion:
            case "pausar":
                db_logger.log_question("pausar spotify")
                spotify.pause_playback()
                update_response_with_delay("Música pausada")
            case "reproducir":
                db_logger.log_question("reproducir spotify")
                spotify.start_playback()
                update_response_with_delay("Reproduciendo música")
            case "siguiente":
                db_logger.log_question("siguiente canción")
                spotify.next_track()
                update_response_with_delay("Siguiente canción")
            case "anterior":
                db_logger.log_question("anterior canción")
                spotify.previous_track()
                update_response_with_delay("Canción anterior")
            case "que_suena":
                db_logger.log_question("qué canción suena")
                track_info = spotify.get_current_track()
                if track_info:
                    nombre_cancion = track_info.split("]")[-1].strip()
                    update_response_with_delay(nombre_cancion)
                else:
                    update_response_with_delay("No se pudo obtener la información de la canción.")
            case _:
                update_response_with_delay("No entendí el comando musical.")
    except Exception as e:
        update_response_with_delay("Hubo un problema con Spotify. Verifica que la aplicación esté abierta y que un dispositivo esté activo.")
        print(f"Error en controlar_musica: {e}")
