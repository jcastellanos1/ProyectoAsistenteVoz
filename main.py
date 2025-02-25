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

# Ruta al modelo en español
MODEL_ES = r"C:\Users\jose5\Desktop\vosk-model-es-0.42"

# Cargar el modelo
if not os.path.exists(MODEL_ES):
    print("Error: No se encontró el modelo en español.")
    sys.exit(1)

model_es = vosk.Model(MODEL_ES)

# Cola para almacenar los datos de audio
q = queue.Queue()

# Inicializar Eel
eel.init('web')

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
        "navegador": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Cambia según tu navegador
        "rola": "https://www.youtube.com/watch?v=nnrp3drhw0k?t=90",  # Inicia en el minuto 1:30
        "lobo": "https://www.youtube.com/watch?v=ckkL7-KPD_E&t=48"  # Inicia en el segundo 48
    }

    for clave, app in aplicaciones.items():
        if clave in comando:
            if app.startswith("http"):
                # Si es una URL, abre en el navegador predeterminado
                print(f"Abriendo URL: {app}")
                webbrowser.open(app)  # Abrir la URL en el navegador
                eel.updateText(f"Abriendo URL: {app}")  # Notificar en la interfaz
            else:
                # Si es una aplicación, abre normalmente
                print(f"Abriendo {clave}...")
                subprocess.run(app, shell=True)  # Abrir la aplicación
                eel.updateText(f"Abriendo {clave}...")  # Notificar en la interfaz
            return

    eel.updateText("No reconocí el comando.")  # Si no coincide con nada

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
                    eel.updateText(f"Has dicho: {texto}")  # Mostrar en la interfaz
                    abrir_aplicacion(texto)  # Intentar abrir una aplicación
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


if __name__ == "__main__":
    try:
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
