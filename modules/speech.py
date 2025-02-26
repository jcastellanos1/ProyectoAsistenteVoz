import os
import queue
import sys
import vosk
import json
import sounddevice as sd

# Ruta al modelo en español
MODEL_ES = r"D:\Proyectos\vosk-model-small-es-0.42"

# Cargar el modelo
if not os.path.exists(MODEL_ES):
    print("Error: No se encontró el modelo en español.")
    sys.exit(1)

model_es = vosk.Model(MODEL_ES)

# Cola para almacenar datos de audio
q = queue.Queue()

def callback(indata, frames, time, status):
    """Función de callback para capturar audio."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

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
                if texto:
                    print(f"Has dicho: {texto}")
                    procesar_comando(texto)  # Llama a la función de ejecución de comandos
