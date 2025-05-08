
import requests

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
        "Eres un sistema de clasificación de comandos por voz para un asistente virtual.\n"
        "Tu tarea es identificar con precisión la intención del usuario y la entidad relevante.\n"
        "Debes responder únicamente con dos líneas:\n"
        "- Línea 1: una de las siguientes intenciones (sin comillas):\n"
        "  abrir_app, cerrar_app, reproducir_musica, volumen, brillo, clima, chiste, preguntas_frecuentes, pregunta_ia, desconocido\n"
        "- Línea 2: la entidad correspondiente (ej: 'Spotify', 'bloc de notas') o 'null' si no aplica.\n"
        "Ejemplos:\n"
        "Entrada: abre Spotify\n"
        "abrir_app\nSpotify\n"
        "Entrada: cuéntame un chiste\n"
        "chiste\nnull\n"
        "Entrada: cuál es el clima en Madrid mañana\n"
        "clima\nMadrid\n"
        "Entrada: qué opinas de la inteligencia artificial\n"
        "pregunta_ia\nnull\n"
        f"Entrada: {texto_usuario}\n"
        "Respuesta:"
    )

    datos = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0,
        "stop": ["Entrada:"]
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=datos)
        contenido = response.json()["response"]
        print("Salida del modelo:", contenido)

        lineas = contenido.strip().splitlines()
        intencion = lineas[0].strip().lower()
        entidad = lineas[1].strip() if len(lineas) > 1 else None
        entidad = None if entidad.lower() == "null" else entidad

        return intencion, entidad

    except Exception as e:
        print("Error al clasificar intención:", e)
        return "desconocido", None
