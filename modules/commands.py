import eel
import subprocess
import webbrowser
import psutil  # Para cerrar aplicaciones
from word2number import w2n
from modules.spotify_control import SpotifyControl

spotify = SpotifyControl()

# Diccionario de aplicaciones
APLICACIONES = {
    "calculadora": {"exe": "calc.exe"},
    "bloc de notas": {"exe": "notepad.exe"},
    "explorador": {"exe": "explorer.exe"},
    "cmd": {"exe": "cmd.exe"},
    "spotify": {"exe": "spotify.exe"},
    "epic games": {"exe": r"D:\Epic\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"},
    "navegador": {"exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe"},
    "rola": {"url": "https://www.youtube.com/watch?v=nnrp3drhw0k&t=90"},
    "lobo": {"url": "https://www.youtube.com/watch?v=ckkL7-KPD_E&t=48"},
    "criminal": {"url": "https://www.youtube.com/watch?v=VqEbCxg2bNI&t=80"}
}

def convertir_numero(texto):
    """Convierte palabras a números (Ej: 'cincuenta' → 50)."""
    try:
        return w2n.word_to_num(texto)
    except ValueError:
        return None

# Abrir apps
def abrir_aplicacion(nombre):
    """Abre una aplicación o una URL según el diccionario."""
    app = APLICACIONES.get(nombre)
    if app:
        if "exe" in app:
            subprocess.Popen(app["exe"], shell=True)
            eel.updateResponse(f"Abriendo {nombre}...")
        elif "url" in app:
            webbrowser.open(app["url"])
            eel.updateResponse(f"Reproduciendo {nombre}...")
    else:
        eel.updateResponse(f"No tengo registrado {nombre}.")

# Cerrar apps
def cerrar_aplicacion(nombre):
    """Cierra una aplicación si está en ejecución."""
    app = APLICACIONES.get(nombre)
    if app and "exe" in app:
        proceso_nombre = app["exe"].split("\\")[-1].lower()  # Extraer solo el nombre del ejecutable en minúsculas
        for proceso in psutil.process_iter(attrs=['pid', 'name']):
            if proceso.info['name'].lower() == proceso_nombre:
                psutil.Process(proceso.info['pid']).terminate()
                eel.updateResponse(f"Cerrando {nombre}...")
                return
        eel.updateResponse(f"{nombre} no está en ejecución.")
    else:
        eel.updateResponse(f"No puedo cerrar {nombre}.")

# Controlar música
def controlar_musica(comando):
    """Ejecuta comandos de música en Spotify."""
    try:
        if "pausa" in comando:
            spotify.pause_playback()
            eel.updateResponse("Música pausada")
        elif "reproducir" in comando:
            spotify.start_playback()
            eel.updateResponse("Reproduciendo música")
        elif "siguiente" in comando:
            spotify.next_track()
            eel.updateResponse("Siguiente canción")
        elif "anterior" in comando:
            spotify.previous_track()
            eel.updateResponse("Canción anterior")
        elif "volumen" in comando:
            palabras = comando.split()
            numeros = [convertir_numero(word) for word in palabras if convertir_numero(word) is not None]
            if numeros:
                vol = numeros[0]
                spotify.set_volume(vol)
                eel.updateResponse(f"Volumen ajustado a {vol}%")
            else:
                eel.updateResponse("No entendí el nivel de volumen.")
        elif "qué suena" in comando:
            track_info = spotify.get_current_track()
            if track_info:
                nombre_cancion = track_info.split("]")[-1].strip()
                eel.updateResponse(f" {nombre_cancion}")
            else:
                eel.updateResponse("No se pudo obtener la información de la canción.")
    except Exception as e:
        eel.updateResponse("Hubo un problema con Spotify. Verifica que la aplicación esté abierta y que un dispositivo esté activo.")
        print(f"Error en controlar_musica: {e}")

# Función para ejecutar comandos
def ejecutar_comando(comando):
    """Procesa el comando de voz y ejecuta la acción correspondiente."""
    eel.updateText(f"Has dicho: {comando}")

    if "reproduce" in comando or "pon" in comando:
        song_name = comando.replace("reproduce", "").replace("pon", "").strip()
        if song_name:
            try:
                respuesta = spotify.start_playback(song_name)
                eel.updateResponse(respuesta)
            except Exception as e:
                eel.updateResponse("Error al reproducir la canción. Verifica si tienes un dispositivo activo en Spotify.")
                print(f"Error en reproducir canción: {e}")
        else:
            eel.updateResponse("No entendí qué canción quieres reproducir.")
        return

    if "cerrar" in comando:
        nombre_app = comando.replace("cerrar", "").strip()
        cerrar_aplicacion(nombre_app)
        return

    if "abrir" in comando:
        nombre_app = comando.replace("abrir", "").strip()
        abrir_aplicacion(nombre_app)
        return

    controlar_musica(comando)
