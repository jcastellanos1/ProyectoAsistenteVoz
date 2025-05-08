import requests
from googletrans import Translator
from modules import db_logger
from modules.commands.comunes import update_response_with_delay

# Mapeo de categorías en español a inglés
categorias = {
    "miedo": "Spooky",
    "programación": "Programming",
    "chiste": "Any",
    "chiste negro": "Dark",
    "navidad": "Christmas",
    "raros": "Misc",
    "raro": "Misc"
}

def extraer_categoria(comando):
    """Extrae la categoría del comando de voz."""
    palabras_categorias = ["miedo", "programación", "chiste negro", "navidad", "raro", "raros"]
    for palabra in palabras_categorias:
        if palabra in comando.lower():
            return palabra
    return "chiste"  # Predeterminado

def contar_chiste(categoria):
    db_logger.log_question(f"contar chiste de {categoria}")
    categoria_ingles = categorias.get(categoria.lower(), "Any")
    
    url = f"https://v2.jokeapi.dev/joke/{categoria_ingles}"
    response = requests.get(url)
    data = response.json()
    
    if not data.get("error"):
        if data["type"] == "twopart":
            chiste = f"{data['setup']} - {data['delivery']}"
        else:
            chiste = data["joke"]
        chiste_traducido = traducir_al_espanol(chiste)
        update_response_with_delay(chiste_traducido, 5)
        return chiste_traducido
    else:
        mensaje_error = f"No pude obtener un chiste de la categoría {categoria}."
        update_response_with_delay(mensaje_error)
        return mensaje_error

def traducir_al_espanol(texto):
    """Traduce un texto de inglés a español."""
    translator = Translator()
    traduccion = translator.translate(texto, src='en', dest='es')
    return traduccion.text
