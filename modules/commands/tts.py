

import pyttsx3
import time

# Inicializa el motor de texto a voz
engine = pyttsx3.init()

def hablar_respuesta(mensaje, delay=0.5):
    """Habla el texto recibido sin controlar la escucha."""
    engine.say(mensaje)
    engine.runAndWait()
    time.sleep(delay)
