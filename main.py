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

# Ruta al modelo en español
MODEL_ES = r"D:\Proyectos\vosk-model-small-es-0.42"

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

def abrir_aplicacion(comando):
    """Abre aplicaciones según el comando de voz."""
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
                print(f"Abriendo URL: {app}")
                webbrowser.open(app)
                eel.updateText(f"Reproduciendo {clave}...")
            else:
                print(f"Abriendo {clave}...")
                subprocess.run(app, shell=True)
                eel.updateText(f"Abriendo {clave}...")
            return
    
    # Comandos de control de Spotify
    if "pausa" in comando:
        spotify.pause_playback()
        eel.updateText("Música pausada")
    elif "reproducir" in comando:
        spotify.start_playback()
        eel.updateText("Reproduciendo música")
    elif "siguiente" in comando:
        spotify.next_track()
        eel.updateText("Siguiente canción")
    elif "anterior" in comando:
        spotify.previous_track()
        eel.updateText("Canción anterior")
    elif "volumen" in comando:
        try:
            vol = int([word for word in comando.split() if word.isdigit()][0])
            spotify.set_volume(vol)
            eel.updateText(f"Volumen ajustado a {vol}%")
        except (IndexError, ValueError):
            eel.updateText("No entendí el nivel de volumen.")
    elif "qué suena" in comando:
        track_info = spotify.get_current_track()
        eel.updateText(track_info)
    else:
        eel.updateText("No reconocí el comando.")

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
