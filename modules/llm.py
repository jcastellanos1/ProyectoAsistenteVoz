
import requests
import json

MODEL_NAME = "gemma3:4b"  

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
        return "No se pudo conectar con el modelo de IA."
    
    
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
        "- Si el usuario dice solo 'reproducir', 'pon música', 'quiero escuchar algo', etc., responde con:\n"
        "  { \"intencion\": \"musica_control\", \"entidad\": \"reproducir\" }\n"
        "- Si el usuario dice 'reproduce [nombre de canción]', la intención es 'reproducir_musica' y la entidad es el nombre de la canción.\n"
        "- Usa 'musica_control' con entidad 'pausar', 'siguiente', 'anterior' o 'que_suena' cuando corresponda.\n"
        "- Si el usuario pregunta 'qué suena', 'qué está sonando', etc., responde con:\n"
        "  { \"intencion\": \"musica_control\", \"entidad\": \"que_suena\" }\n"
        "- Si no comprendes el comando, devuelve:\n"
        "  { \"intencion\": \"desconocido\", \"entidad\": null }\n\n"

        "--- EJEMPLOS ---\n"
        "Usuario: reproducir\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"reproducir\" }\n"
        "Usuario: pon música\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"reproducir\" }\n"
        "Usuario: quiero escuchar algo\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"reproducir\" }\n"
        "Usuario: ponle pausa\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"pausar\" }\n"
        "Usuario: pausa\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"pausar\" }\n"
        "Usuario: siguiente canción\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"siguiente\" }\n"
        "Usuario: anterior\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"anterior\" }\n"
        "Usuario: qué suena\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"que_suena\" }\n"
        "Usuario: qué canción está sonando\n"
        "{ \"intencion\": \"musica_control\", \"entidad\": \"que_suena\" }\n"
        "Usuario: reproduce criminal\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"criminal\" }\n"
        "Usuario: pon 'volveré'\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": \"volveré\" }\n"
        "Usuario: abre Spotify\n"
        "{ \"intencion\": \"abrir_app\", \"entidad\": \"spotify\" }\n"
        "Usuario: cerrar Spotify\n"
        "{ \"intencion\": \"cerrar_app\", \"entidad\": \"spotify\" }\n"
        "Usuario: sube el volumen al 50 porciento\n"
        "{ \"intencion\": \"volumen\", \"entidad\": null }\n"
        "Usuario: baja el brillo\n"
        "{ \"intencion\": \"brillo\", \"entidad\": null }\n"
        "Usuario: clima en Guatemala\n"
        "{ \"intencion\": \"clima\", \"entidad\": \"guatemala\" }\n"
        "Usuario: cuéntame un chiste de miedo\n"
        "{ \"intencion\": \"chiste\", \"entidad\": \"miedo\" }\n"
        "Usuario: qué puedes hacer\n"
        "{ \"intencion\": \"preguntas_frecuentes\", \"entidad\": null }\n"
        "Usuario: qué sabes de python\n"
        "{ \"intencion\": \"pregunta_ia\", \"entidad\": null }\n"
        "Usuario: hola\n"
        "{ \"intencion\": \"desconocido\", \"entidad\": null }\n"

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

        # Validación final (por si el modelo devuelve una intención no válida)
        INTENCIONES_VALIDAS = {
            "abrir_app", "cerrar_app", "reproducir_musica",
            "musica_control", "volumen", "brillo",
            "clima", "chiste", "preguntas_frecuentes",
            "pregunta_ia", "desconocido"
        }

        if intencion not in INTENCIONES_VALIDAS:
            print(f"❌ Intención inválida recibida: {intencion}")
            return "desconocido", None

        return intencion, entidad

    except json.JSONDecodeError as je:
        print("❌ Error de formato JSON:", je)
        print("Contenido recibido:", contenido)
    except Exception as e:
        print("❌ Error al clasificar intención:", e)

    return "desconocido", None

