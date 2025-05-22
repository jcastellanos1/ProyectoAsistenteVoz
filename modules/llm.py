from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Cargar variables de entorno desde .env
load_dotenv()

# Usar la API key desde el entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-3.5-turbo"

prompt_sistema = (
    "Eres Aurora, un asistente virtual inteligente. Tu función es ayudar al usuario resolviendo dudas, "
    "explicando conceptos de forma clara, y respondiendo de manera breve, útil y profesional.\n"
    "Siempre responde en español. Si la pregunta es ambigua, pide aclaración. "
    "No des rodeos innecesarios y evita responder cosas que no te han sido preguntadas. Sé amable pero directo."
)

historial = []

def obtener_respuesta_ia(pregunta):
    global historial

    contexto = [{"role": "system", "content": prompt_sistema}]
    contexto += historial[-6:]
    contexto.append({"role": "user", "content": pregunta})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=contexto,
            temperature=0.6,
            top_p=0.9
        )
        texto = response.choices[0].message.content.strip()

        historial.append({"role": "user", "content": pregunta})
        historial.append({"role": "assistant", "content": texto})
        if len(historial) > 12:
            historial = historial[-12:]

        return texto
    except Exception as e:
        print("❌ Error al conectarse con ChatGPT:", e)
        return "No se pudo conectar con el modelo de IA."

# --------------------------------------------------------

def limpiar_respuesta_json(texto):
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
    "- \"entidad\": el valor relevante si aplica (como nombre de app, canción, ciudad, nivel, dirección), o bien 'subir', 'bajar' o null.\n\n"
    "--- INSTRUCCIONES ESPECIALES ---\n"
    "- Si el usuario dice 'sube el volumen', 'baja el brillo', 'aumenta', 'reduce', etc., responde con:\n"
    "  intencion: 'volumen' o 'brillo'\n"
    "  entidad: 'subir' o 'bajar'\n"
    "- Si dice 'pon el volumen en 50%', responde con entidad null (el sistema lo interpretará como valor).\n"
    "- Si no comprendes el comando, responde con:\n"
    "  { \"intencion\": \"desconocido\", \"entidad\": null }\n\n"

    "--- EJEMPLOS ---\n"
    "Usuario: sube el volumen\n"
    "{ \"intencion\": \"volumen\", \"entidad\": \"subir\" }\n"
    "Usuario: baja el brillo\n"
    "{ \"intencion\": \"brillo\", \"entidad\": \"bajar\" }\n"
    "Usuario: pon el volumen en cincuenta\n"
    "{ \"intencion\": \"volumen\", \"entidad\": null }\n"
    "Usuario: baja un poco el volumen\n"
    "{ \"intencion\": \"volumen\", \"entidad\": \"bajar\" }\n"
    "Usuario: aumenta el brillo\n"
    "{ \"intencion\": \"brillo\", \"entidad\": \"subir\" }\n"
    "Usuario: quiero un chiste\n"
    "{ \"intencion\": \"chiste\", \"entidad\": null }\n"
    "Usuario: qué canción está sonando\n"
    "{ \"intencion\": \"musica_control\", \"entidad\": \"que_suena\" }\n"
    "Usuario: qué sabes de python\n"
    "{ \"intencion\": \"pregunta_ia\", \"entidad\": null }\n"
    "Usuario: hola\n"
    "{ \"intencion\": \"desconocido\", \"entidad\": null }\n"

    "--- ENTRADA ACTUAL ---\n"
    f"Usuario: {texto_usuario}\n"
    "Respuesta:"
)


    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Devuelve solo un JSON con los campos intencion y entidad."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        contenido = response.choices[0].message.content.strip()
        print("Salida del modelo:", contenido)

        contenido = limpiar_respuesta_json(contenido)
        parsed = json.loads(contenido)

        intencion = parsed.get("intencion", "desconocido").lower()
        entidad = parsed.get("entidad")
        entidad = None if entidad in [None, "null"] else entidad

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
