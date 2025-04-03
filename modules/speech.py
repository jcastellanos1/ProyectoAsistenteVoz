import os
import queue
import sys
import vosk
import json
from dotenv import load_dotenv
import sounddevice as sd


load_dotenv()

# Ruta al modelo en español
MODEL_ES = os.getenv("URL_VOSK_MODEL")

# Cargar el modelo
if not os.path.exists(MODEL_ES):
    print("Error: No se encontró el modelo en español.")
    sys.exit(1)

model_es = vosk.Model(MODEL_ES)

# Cola para almacenar datos de audio
q = queue.Queue()

# Variable global para controlar el estado de escucha
is_listening = True

def set_listening_state(state):
    """Controla el estado de escucha del reconocimiento de voz."""
    global is_listening
    is_listening = state

def callback(indata, frames, time, status):
    """Función de callback para capturar audio."""
    global is_listening
    if status:
        print(status, file=sys.stderr)
    if is_listening:
        q.put(bytes(indata))
    else:
        q.put(bytes(b'\x00' * len(indata)))  # Enviar silencio cuando no está escuchando

def reconocer_voz(procesar_comando):
    """Reconoce voz en tiempo real y ejecuta comandos."""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Escuchando... Habla ahora.")
        rec_es = vosk.KaldiRecognizer(model_es, 16000)

        while True:
            data = q.get()
            if rec_es.AcceptWaveform(data):
                result = json.loads(rec_es.Result())
                texto = result.get("text", "")
                if texto and is_listening:
                    print(f"Has dicho: {texto}")
                    set_listening_state(False)  # Pausar escucha antes de procesar
                    procesar_comando(texto)
                    set_listening_state(True)  # Reanudar escucha después de procesar
