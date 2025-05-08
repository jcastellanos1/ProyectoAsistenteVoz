
from word2number import w2n
from modules import db_logger
import eel
from modules.commands.tts import hablar_respuesta

def convertir_numero(texto):
    """Convierte palabras a números (Ej: 'cincuenta' → 50)."""
    try:
        return w2n.word_to_num(texto)
    except ValueError:
        return None


def responder_preguntas_frecuentes():
    top = db_logger.obtener_top_preguntas()
    
    if not top:
        respuesta = "Aún no tengo preguntas registradas."
    else:
        preguntas = [q[0].capitalize() for q in top]
        respuesta = "Las preguntas más comunes son: " + ", ".join(preguntas) + "."

    update_response_with_delay(respuesta, 5)

def responder_preguntas_menos_frecuentes():
    menos_frecuentes = db_logger.obtener_low_preguntas()
    
    if not menos_frecuentes:
        respuesta = "Aún no tengo preguntas registradas."
    else:
        preguntas = [q[0].capitalize() for q in menos_frecuentes]
        respuesta = "Las preguntas menos comunes son: " + ", ".join(preguntas) + "."

    update_response_with_delay(respuesta, 5)



def update_response_with_delay(mensaje, delay=1):
    """Actualiza la respuesta en el frontend y la pronuncia en voz alta."""
    eel.updateResponse(mensaje)       # Muestra mensaje en pantalla
    hablar_respuesta(mensaje, delay)  # Lo dice en voz alta (y pausa escucha)
