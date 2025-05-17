import os
import queue
import sys
import vosk
import json
import re
from dotenv import load_dotenv
import sounddevice as sd
import threading

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
    print(f"[DEBUG] Estado de escucha: {state}")
    global is_listening
    is_listening = state

def es_texto_valido(texto):
    """Filtra entradas irrelevantes como muletillas o frases vacías."""
    texto = texto.strip().lower()
    patrones_ignorados = r"^(eh+|ah+|mm+|aja+|sí+|no+|ok+|vale+|gracias+|ya|listo)$"
    return bool(texto and len(texto.split()) > 1 and not re.fullmatch(patrones_ignorados, texto))

def callback(indata, frames, time, status):
    """Función de callback para capturar audio."""
    global is_listening
    if status:
        print(status, file=sys.stderr)
    if is_listening:
        q.put(bytes(indata))
    # No enviar silencio, para evitar confundir al reconocedor

def reconocer_voz(procesar_comando):
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Escuchando... Habla ahora.")
        rec_es = vosk.KaldiRecognizer(model_es, 16000)

        while True:
            if not is_listening:
                sd.sleep(100)  # Pausa breve si está en modo silencio
                continue

            data = q.get()
            if rec_es.AcceptWaveform(data):
                result = json.loads(rec_es.Result())
                texto = result.get("text", "")
                if es_texto_valido(texto):
                    print(f"Has dicho: {texto}")
                    threading.Thread(target=procesar_comando, args=(texto,), daemon=True).start()
                else:
                    print(f"(Ignorado): {texto}")
