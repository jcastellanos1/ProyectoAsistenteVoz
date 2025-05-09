
import requests
import json


MODEL_NAME = "gemma3:1b"  


prompt_sistema = (
    "Eres Aurora, un asistente virtual inteligente. Tu función es ayudar al usuario resolviendo dudas, "
    "explicando conceptos de forma clara, y respondiendo de manera breve, útil y profesional.\n"
    "Siempre responde en español. Si la pregunta es ambigua, pide aclaración. "
    "No des rodeos innecesarios y evita responder cosas que no te han sido preguntadas. Sé amable pero directo.\n"
    "Ejemplos:\n"
    "Usuario: ¿Cuál es la capital de Guatemala?\n"
    "Asistente: La capital de Guatemala es Ciudad de Guatemala.\n"
    "Usuario: ¿Qué significa inteligencia artificial?\n"
    "Asistente: Es la capacidad de una máquina para realizar tareas que normalmente requieren inteligencia humana, como aprender o razonar.\n"
)


historial = []

def obtener_respuesta_ia(pregunta):
    global historial

    contexto = "\n".join(historial[-6:])
    prompt = f"{prompt_sistema}\n{contexto}\nUsuario: {pregunta}\nAsistente:"

    datos = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.6,
        "top_k": 40,
        "top_p": 0.9,
        "stop": ["Usuario:", "Asistente:"]
    }

    try:
        respuesta = requests.post("http://localhost:11434/api/generate", json=datos)
        texto = respuesta.json()["response"].strip()

        
        historial.append(f"Usuario: {pregunta}")
        historial.append(f"Asistente: {texto}")
        if len(historial) > 12:
            historial.pop(0)
            historial.pop(0)

        return texto
    except Exception as e:
        print("Error al conectarse con Ollama:", e)
        return "⚠️ No se pudo conectar con el modelo de IA."
    
    
def limpiar_respuesta_json(texto):
    """Elimina bloques tipo Markdown como ```json ...``` del resultado."""
    texto = texto.strip()
    if texto.startswith("```json"):
        texto = texto.replace("```json", "").replace("```", "").strip()
    elif texto.startswith("```"):
        texto = texto.replace("```", "").strip()
    return texto

def obtener_intencion(texto_usuario):
    prompt = (
        "Eres un clasificador de intenciones para un asistente virtual por voz.\n"
        "Tu objetivo es analizar el comando del usuario y devolver únicamente un objeto JSON con dos campos:\n"
        "- \"intencion\": una de las siguientes opciones válidas:\n"
        "  abrir_app, cerrar_app, reproducir_musica, musica_control, volumen, brillo, clima, chiste, preguntas_frecuentes, pregunta_ia, desconocido\n"
        "- \"entidad\": el valor relevante si aplica (como nombre de app, canción, ciudad, categoría), o null si no corresponde.\n\n"
        "IMPORTANTE: No agregues texto adicional antes ni después del JSON. Solo responde con el objeto JSON.\n\n"

        "--- INSTRUCCIONES ESPECIALES ---\n"
        "- Si el comando contiene las palabras exactas: pausa, siguiente, anterior, que suena o reproduce (solas), usa 'musica_control'.\n"
        "- Si el comando tiene 'reproduce' o 'pon' seguido de un nombre de canción, incluso entre comillas, usa 'reproducir_musica'.\n"
        "- La entidad puede contener varias palabras o estar entre comillas simples o dobles.\n\n"

        "--- EJEMPLOS ---\n"

        # Control de música
        "Usuario: siguiente\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"siguiente\" }\n"
        "Usuario: pausa\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"pausar\" }\n"
        "Usuario: anterior\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"anterior\" }\n"
        "Usuario: que suena\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"que_suena\" }\n"
        "Usuario: reproduce\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"reproducir\" }\n"

        # Reproducir canciones
        "Usuario: reproduce la incondicional\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"la incondicional\" }\n"
        "Usuario: pon \"La incondicional\"\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"la incondicional\" }\n"
        "Usuario: reproduce 'volveré'\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"volveré\" }\n"
        "Usuario: pon a dónde vamos a parar\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"a dónde vamos a parar\" }\n"
        "Usuario: pon me haces falta\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"me haces falta\" }\n"

        # Abrir/cerrar aplicaciones
        "Usuario: abre Spotify\n"
        "{ \"intencion\": \"abrir_app\", \"entidad\": \"spotify\" }\n"
        "Usuario: abrir bloc de notas\n"
        "{ \"intencion\": \"abrir_app\", \"entidad\": \"bloc de notas\" }\n"
        "Usuario: cerrar Spotify\n"
        "{ \"intencion\": \"cerrar_app\", \"entidad\": \"spotify\" }\n"
        "Usuario: cierra el navegador\n"
        "{ \"intencion\": \"cerrar_app\", \"entidad\": \"navegador\" }\n"

        # Volumen y brillo
        "Usuario: sube el volumen al 50 porciento\n"
        "{ \"intencion\": \"volumen\", \"entidad\": null }\n"
        "Usuario: baja el volumen\n"
        "{ \"intencion\": \"volumen\", \"entidad\": null }\n"
        "Usuario: subir brillo\n"
        "{ \"intencion\": \"brillo\", \"entidad\": null }\n"
        "Usuario: baja el brillo al 30\n"
        "{ \"intencion\": \"brillo\", \"entidad\": null }\n"

        # Clima
        "Usuario: clima mañana\n"
        "{ \"intencion\": \"clima\", \"entidad\": null }\n"
        "Usuario: clima hoy\n"
        "{ \"intencion\": \"clima\", \"entidad\": null }\n"
        "Usuario: clima\n"
        "{ \"intencion\": \"clima\", \"entidad\": null }\n"
        "Usuario: cuál es el clima\n"
        "{ \"intencion\": \"clima\", \"entidad\": null }\n"
        "Usuario: clima en Guatemala\n"
        "{ \"intencion\": \"clima\", \"entidad\": \"guatemala\" }\n"
        "Usuario: qué clima hará en Ciudad de Guatemala\n"
        "{ \"intencion\": \"clima\", \"entidad\": \"ciudad de guatemala\" }\n"

        # Chistes
        "Usuario: cuéntame un chiste\n"
        "{ \"intencion\": \"chiste\", \"entidad\": null }\n"
        "Usuario: cuéntame un chiste de miedo\n"
        "{ \"intencion\": \"chiste\", \"entidad\": \"miedo\" }\n"
        "Usuario: dime un chiste navideño\n"
        "{ \"intencion\": \"chiste\", \"entidad\": \"navidad\" }\n"

        # Preguntas frecuentes y generales
        "Usuario: qué puedes hacer\n"
        "{ \"intencion\": \"preguntas_frecuentes\", \"entidad\": null }\n"
        "Usuario: para qué sirves\n"
        "{ \"intencion\": \"preguntas_frecuentes\", \"entidad\": null }\n"
        "Usuario: qué sabes de python\n"
        "{ \"intencion\": \"pregunta_ia\", \"entidad\": null }\n"
        "Usuario: cómo funciona la inteligencia artificial\n"
        "{ \"intencion\": \"pregunta_ia\", \"entidad\": null }\n"

        "--- ENTRADA ACTUAL ---\n"
        f"Usuario: {texto_usuario}\n"
        "Respuesta:"
    )



    datos = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0,
        "stop": ["Usuario:"]
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=datos)
        contenido = response.json().get("response", "").strip()

        if not contenido:
            raise ValueError("La respuesta del modelo está vacía.")

        print("Salida del modelo:", contenido)

        contenido = limpiar_respuesta_json(contenido)
        parsed = json.loads(contenido)

        intencion = parsed.get("intencion", "desconocido").lower()
        entidad = parsed.get("entidad")
        entidad = None if entidad in [None, "null"] else entidad

        return intencion, entidad

    except json.JSONDecodeError as je:
        print("❌ Error de formato JSON:", je)
        print("Contenido recibido:", contenido)
    except Exception as e:
        print("❌ Error al clasificar intención:", e)

    return "desconocido", None