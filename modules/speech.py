import os
import queue
import sys
import vosk
import json
import re
import sounddevice as sd
import threading
from dotenv import load_dotenv

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
    print(f"[DEBUG] Estado de escucha: {state}")

# Comandos válidos de una sola palabra
COMANDOS_VALIDOS = {
    "reproducir", "pausar", "siguiente", "anterior", "que", "suena",
    "sube", "baja", "clima", "brillo", "volumen", "pon", "abre", "cierra"
}

# Frases o sonidos comunes que deben ignorarse
IGNORADOS_EXACTOS = {
    "eh", "ah", "mm", "aja", "sí", "no", "ok", "vale", "gracias", "ya", "listo", ""
}

def es_texto_valido(texto):
    """Evalúa si el texto reconocido debe ser procesado o ignorado."""
    texto = texto.strip().lower()
    if texto in IGNORADOS_EXACTOS:
        return False
    if len(texto.split()) > 1:
        return True
    return texto in COMANDOS_VALIDOS

def callback(indata, frames, time, status):
    """Callback de audio para capturar sonido."""
    global is_listening
    if status:
        print(status, file=sys.stderr)
    if is_listening:
        q.put(bytes(indata))

def reconocer_voz(procesar_comando):
    """Inicia la captura de audio y procesamiento de comandos con Vosk."""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Escuchando... Habla ahora.")
        rec_es = vosk.KaldiRecognizer(model_es, 16000)

        while True:
            if not is_listening:
                sd.sleep(100)
                continue

            data = q.get()
            if rec_es.AcceptWaveform(data):
                result = json.loads(rec_es.Result())
                texto = result.get("text", "").strip()

                if es_texto_valido(texto):
                    print(f"Has dicho: {texto}")
                    threading.Thread(target=procesar_comando, args=(texto,), daemon=True).start()
                else:
                    print(f"(Ignorado): {texto}")
