import os
import queue
import sys
import sounddevice as sd
import vosk
import json
import threading
import subprocess
import eel
import webbrowser
from flask import Flask, jsonify, request
from spotify_control import SpotifyControl  # Importar la clase de control de Spotify
from word2number import w2n

# Ruta al modelo en español
MODEL_ES = r"C:\Users\jose5\Desktop\vosk-model-small-es-0.42"

# Cargar el modelo
if not os.path.exists(MODEL_ES):
    print("Error: No se encontró el modelo en español.")
    sys.exit(1)

model_es = vosk.Model(MODEL_ES)

# Cola para almacenar los datos de audio
q = queue.Queue()

# Inicializar Eel
eel.init('web')

# Inicializar control de Spotify
spotify = SpotifyControl()

# Inicializar Flask para el control de Spotify
app = Flask(__name__)

def callback(indata, frames, time, status):
    """Función de callback para capturar audio en tiempo real."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def convertir_numero(texto):
    try:
        return w2n.word_to_num(texto)  # Convierte "cincuenta" → 50
    except ValueError:
        return None
    

def abrir_aplicacion(comando):
    """Ejecuta acciones según el comando de voz."""
    eel.updateText(f"Has dicho: {comando}")  # Mostrar lo que el asistente escucha

    if "reproduce" in comando or "pon" in comando:
        song_name = comando.replace("reproduce", "").replace("pon", "").strip()
        if song_name:
            respuesta = spotify.start_playback(song_name)
            eel.updateResponse(respuesta)  # Mostrar y hablar la respuesta
        else:
            eel.updateResponse("No entendí qué canción quieres reproducir.")
    
    elif "spotify" in comando:
        spotify.start_playback()
        eel.updateResponse("Abriendo Spotify...")

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
                eel.updateResponse(f"Abriendo {clave}...")
                subprocess.run(app, shell=True)
                #eel.updateResponse(f"Abriendo {clave}...")
            return  # Evita seguir evaluando otros comandos

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
            # Limpiar el texto reconocido (eliminar códigos o caracteres no deseados)
            nombre_cancion = track_info.split("]")[-1].strip()  # Eliminar todo antes del último "]"
            eel.updateResponse(f" {nombre_cancion}")  # Mostrar solo el nombre de la canción
        else:
            eel.updateResponse("No se pudo obtener la información de la canción.")

def reconocer_voz():
    """Reconocer voz en tiempo real."""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Escuchando... Habla ahora.")
        rec_es = vosk.KaldiRecognizer(model_es, 16000)
        while True:
            data = q.get()
            if rec_es.AcceptWaveform(data):
                result = json.loads(rec_es.Result())
                texto = result.get("text", "")
                if texto:
                    print(f"Has dicho: {texto}")
                    eel.updateText(f"Has dicho: {texto}")
                    abrir_aplicacion(texto)
            else:
                partial_result = json.loads(rec_es.PartialResult())
                partial_text = partial_result.get("partial", "")
                if partial_text:
                    print(f"Escuchando: {partial_text}", end='\r')
                    eel.updateText(f"Escuchando: {partial_text}")

@eel.expose
def start_listening():
    """Iniciar el reconocimiento de voz en un hilo separado."""
    threading.Thread(target=reconocer_voz, daemon=True).start()

def run_flask():
    """Ejecutar Flask en un hilo separado."""
    app.run(port=8080, debug=False, use_reloader=False)

if __name__ == "__main__":
    try:
        # Ejecutar Flask en un hilo separado
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Obtener tamaño de pantalla
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        
        # Definir el tamaño de la ventana
        win_width, win_height = 500, 700
        
        # Calcular la posición centrada
        pos_x = (screen_width - win_width) // 2
        pos_y = (screen_height - win_height) // 2
        
        # Iniciar Eel con la ventana centrada
        eel.start("index.html", mode="chrome", size=(win_width, win_height), position=(pos_x, pos_y))
    except KeyboardInterrupt:
        print("\nPrograma terminado.")
