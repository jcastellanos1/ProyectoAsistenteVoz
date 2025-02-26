import eel
import subprocess
import webbrowser
from word2number import w2n
from modules.spotify_control import SpotifyControl

spotify = SpotifyControl()

def convertir_numero(texto):
    try:
        return w2n.word_to_num(texto)  # Convierte "cincuenta" → 50
    except ValueError:
        return None

def ejecutar_comando(comando):
    """Ejecuta acciones según el comando de voz."""
    eel.updateText(f"Has dicho: {comando}")

    if "reproduce" in comando or "pon" in comando:
        song_name = comando.replace("reproduce", "").replace("pon", "").strip()
        if song_name:
            respuesta = spotify.start_playback(song_name)
            eel.updateResponse(respuesta)
        else:
            eel.updateResponse("No entendí qué canción quieres reproducir.")
        return

    aplicaciones = {
        "calculadora": "calc.exe",
        "bloc de notas": "notepad.exe",
        "explorador": "explorer.exe",
        "cmd": "cmd.exe",
        "spotify": "spotify.exe",
        "epic games": r"D:\Epic\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        "navegador": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "rola": "https://www.youtube.com/watch?v=nnrp3drhw0k&t=90",
        "lobo": "https://www.youtube.com/watch?v=ckkL7-KPD_E&t=48",
        "criminal": "https://www.youtube.com/watch?v=VqEbCxg2bNI&t=80"
    }

    for clave, app in aplicaciones.items():
        if clave in comando:
            if app.startswith("http"):
                webbrowser.open(app)
                eel.updateResponse(f"Reproduciendo {clave}...")
            else:
                subprocess.run(app, shell=True)
                eel.updateResponse(f"Abriendo {clave}...")
            return

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
    elif "que suena" in comando:
        track_info = spotify.get_current_track()
        if track_info:
            nombre_cancion = track_info.split("]")[-1].strip()
            eel.updateResponse(f" {nombre_cancion}")
        else:
            eel.updateResponse("No se pudo obtener la información de la canción.")
