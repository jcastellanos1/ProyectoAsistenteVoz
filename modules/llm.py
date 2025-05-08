
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
def obtener_intencion(texto_usuario):
    prompt = (
        "Tu tarea es analizar el mensaje del usuario y devolver un JSON con la intención y, si aplica, una entidad clave.\n"
        "Debes usar solo una de estas intenciones: abrir_app, cerrar_app, reproducir_musica, volumen, brillo, clima, chiste, preguntas_frecuentes, pregunta_ia, desconocido.\n"
        "Si el mensaje no corresponde claramente a una intención, responde con 'desconocido'.\n"
        "Formato de respuesta (solo JSON):\n"
        "{ \"intencion\": \"abrir_app\", \"entidad\": \"bloc de notas\" }\n"
        "Ejemplos:\n"
        "Usuario: abre Spotify\n"
        "{ \"intencion\": \"abrir_app\", \"entidad\": \"spotify\" }\n"
        "Usuario: cuéntame un chiste\n"
        "{ \"intencion\": \"chiste\", \"entidad\": null }\n"
        "Usuario: cuál es el clima en Madrid\n"
        "{ \"intencion\": \"clima\", \"entidad\": \"Madrid\" }\n"
        "Usuario: quiero escuchar música\n"
        "{ \"intencion\": \"reproducir_musica\", \"entidad\": null }\n"
        "Usuario: quiero que habrás bloc de notas\n"
        "{ \"intencion\": \"abrir_app\", \"entidad\": \"bloc de notas\" }\n"
        "Usuario: qué opinas de la IA\n"
        "{ \"intencion\": \"pregunta_ia\", \"entidad\": null }\n"
        f"Usuario: {texto_usuario}\n"
        "Respuesta JSON:"
    )

    datos = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0,
        "stop": ["Usuario:", "Asistente:", "\n\n"]
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=datos)
        contenido = response.json()["response"]
        print("Respuesta cruda del modelo:", contenido)

        resultado = json.loads(contenido)
        print("Intención detectada (JSON):", json.dumps(resultado, indent=2, ensure_ascii=False))
        return resultado

    except Exception as e:
        print("Error al clasificar intención:", e)
        return {"intencion": "desconocido", "entidad": None}