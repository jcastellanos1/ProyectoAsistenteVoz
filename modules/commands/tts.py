import pyttsx3
import threading
import time

engine = pyttsx3.init()
voz_lock = threading.Lock()

def hablar_respuesta(texto, delay=1):
    time.sleep(delay)
    with voz_lock:
        engine.say(texto)
        engine.runAndWait()
