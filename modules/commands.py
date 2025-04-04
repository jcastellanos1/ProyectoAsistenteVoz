import eel
import random
import subprocess
import webbrowser
import psutil  # Para cerrar aplicaciones
import screen_brightness_control as sbc
from word2number import w2n
from modules.spotify_control import SpotifyControl
from modules.weather import get_weather, get_forecast 
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import re
import requests
from googletrans import Translator
from modules.speech import set_listening_state
import time
from modules import db_logger

VALORES_NIVELES = {
    "cero": 0,
    "diez": 10,
    "veinte": 20,
    "treinta": 30,
    "cuarenta": 40,
    "cincuenta": 50,
    "sesenta": 60,
    "setenta": 70,
    "ochenta": 80,
    "noventa": 90,
    "cien": 100
}

# Diccionario de aplicaciones
APLICACIONES = {
    "calculadora": {"exe": "calc.exe"},
    "bloc de notas": {"exe": "notepad.exe"},
    "explorador": {"exe": "explorer.exe"},
    "terminal": {"exe": "cmd.exe"},
    "spotify": {"exe": "spotify.exe"},
    "epic games": {"exe": r"D:\Epic\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"},
    "navegador": {"exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe"},
    "rola": {"url": "https://www.youtube.com/watch?v=nnrp3drhw0k&t=90"},
    "lobo": {"url": "https://www.youtube.com/watch?v=ckkL7-KPD_E&t=48"},
    "criminal": {"url": "https://www.youtube.com/watch?v=VqEbCxg2bNI&t=80"}
}

spotify = SpotifyControl()

#mapear categorías en español a inglés
categorias = {
    "miedo": "Spooky",
    "programación": "Programming",
    "chiste": "Any",
    "chiste negro": "Dark",
    "navidad": "Christmas",
    "raros": "Misc",
    "raro": "Misc"
    # Agrega más categorías según sea necesario
}

def traducir_al_espanol(texto):
    """Traduce un texto de inglés a español."""
    translator = Translator()
    traduccion = translator.translate(texto, src='en', dest='es')
    return traduccion.text

def update_response_with_delay(mensaje, delay=1):
    """Actualiza la respuesta en la interfaz y espera antes de reactivar el reconocimiento."""
    eel.updateResponse(mensaje)
    time.sleep(delay)  # Espera el tiempo especificado
    set_listening_state(True)

def responder_preguntas_frecuentes():
    top = db_logger.obtener_top_preguntas()
    
    if not top:
        respuesta = "Aún no tengo preguntas registradas."
    else:
        respuesta = "Las preguntas más comunes que usas son: "
        preguntas = [q[0] for q in top]
        respuesta += ", ".join(preguntas)

    update_response_with_delay(respuesta, 5)



def responder_preguntas_menos_frecuentes():
    menos = db_logger.obtener_preguntas_menos_frecuentes()
    
    if not menos:
        respuesta = "Aún no tengo suficientes preguntas registradas."
    else:
        respuesta = "Las preguntas menos frecuentes son: "
        preguntas = [q[0] for q in menos]
        respuesta += ", ".join(preguntas)

    update_response_with_delay(respuesta, 5)


def contar_chiste(categoria):
    db_logger.log_question(f"contar un chiste de ")
    """Obtiene un chiste de la categoría especificada y lo muestra."""
    categoria_ingles = categorias.get(categoria.lower(), "Any") 
   
    if categoria_ingles == "Any":
        print("No se encontró categoría válida. Usando 'Any'.")
    
    url = f"https://v2.jokeapi.dev/joke/{categoria_ingles}"
    response = requests.get(url)
    data = response.json()
    
    print(f"Solicitud a la API para la categoría: {categoria_ingles}")
    print(f"Respuesta de la API: {data}")
    
    if data["error"] == False:
        if data["type"] == "twopart":
            pregunta = data["setup"]
            respuesta = data["delivery"]
            chiste = f"{pregunta} - {respuesta}"
        else:
            chiste = data["joke"]
        
        chiste_traducido = traducir_al_espanol(chiste)
        update_response_with_delay(chiste_traducido, 5)  # Más tiempo para chistes largos
        return chiste_traducido
    else:
        mensaje_error = f"No pude obtener un chiste de la categoría {categoria}."
        update_response_with_delay(mensaje_error)
        return mensaje_error

def ajustar_nivel(comando):
    """Ajusta el volumen o brillo basado en un comando flexible."""
    comando = comando.lower()

    # Buscar tipo (volumen o brillo)
    tipo = None
    if "volumen" in comando:
        tipo = "volumen"
    elif "brillo" in comando:
        tipo = "brillo"

    # Buscar acción (subir o bajar)
    accion = None
    if "subir" in comando or "aumentar" in comando:
        accion = "subir"
    elif "bajar" in comando or "reducir" in comando or "disminuir" in comando:
        accion = "bajar"

    # Buscar valor en cualquier parte del texto
    valor = None
    for palabra, numero in VALORES_NIVELES.items():
        if re.search(rf'\b{palabra}\b', comando):
            valor = numero
            break

    # Validar si se encontró todo lo necesario
    if tipo and accion and valor is not None:
        if tipo == "volumen":
            ajustar_volumen(valor)
        elif tipo == "brillo":
            ajustar_brillo(valor)
    else:
        update_response_with_delay("No entendí el comando correctamente.")
                           
def clima_comando(city="Santa Lucía Cotzumalguapa, GT"):
    """Comando para obtener el clima actual de una ciudad."""
    print(get_weather(city))  # Muestra el clima actual
    update_response_with_delay(get_weather(city))

def pronostico_comando(city="Santa Lucía Cotzumalguapa, GT", days=3):
    """Comando para obtener el pronóstico de clima para los próximos días."""
    print(get_forecast(city, days))  # Muestra el pronóstico para los próximos días
    update_response_with_delay(get_forecast(city, days))

def clima_ciudad_comando(city):
    """Comando para obtener el clima actual de una ciudad específica."""
    print(get_weather(city))  # Muestra el clima actual de la ciudad especificada
    update_response_with_delay(get_weather(city))

def pronostico_ciudad_comando(city, days=3):
    db_logger.log_question(f"Pronostico en ")
    """Comando para obtener el pronóstico de clima de una ciudad específica."""
    print(get_forecast(city, days))  # Muestra el pronóstico para los próximos días de la ciudad especificada
    update_response_with_delay(get_forecast(city, days))

def convertir_numero(texto):
    """Convierte palabras a números (Ej: 'cincuenta' → 50)."""
    try:
        return w2n.word_to_num(texto)
    except ValueError:
        return None

# Abrir apps
def abrir_aplicacion(nombre):
    db_logger.log_question(f"abrir aplicacion")
    """Abre una aplicación o una URL según el diccionario."""
    app = APLICACIONES.get(nombre)
    if app:
        if "exe" in app:
            subprocess.Popen(app["exe"], shell=True)
            update_response_with_delay(f"Abriendo {nombre}...")
        elif "url" in app:
            webbrowser.open(app["url"])
            update_response_with_delay(f"Reproduciendo {nombre}...")
    else:
        update_response_with_delay(f"No tengo registrado {nombre}.")

# Cerrar apps
def cerrar_aplicacion(nombre):
    db_logger.log_question(f"cerrar apliacion")
    """Cierra una aplicación si está en ejecución."""
    app = APLICACIONES.get(nombre)
    if app and "exe" in app:
        proceso_nombre = app["exe"].split("\\")[-1].lower()  # Extraer solo el nombre del ejecutable en minúsculas
        for proceso in psutil.process_iter(attrs=['pid', 'name']):
            if proceso.info['name'].lower() == proceso_nombre:
                psutil.Process(proceso.info['pid']).terminate()
                update_response_with_delay(f"Cerrando {nombre}...")
                return
        update_response_with_delay(f"{nombre} no está en ejecución.")
    else:
        update_response_with_delay(f"No puedo cerrar {nombre}.")

# COntrol volumen
def ajustar_volumen(porcentaje):
    """Ajusta el volumen del sistema al porcentaje especificado (0-100)."""
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    # Normalizar el volumen al rango entre 0.0 y 1.0
    volumen.SetMasterVolumeLevelScalar(porcentaje / 100, None)
    update_response_with_delay(f"Volumen ajustado a {porcentaje}%")

def subir_volumen(incremento=10):
    db_logger.log_question(f"subir volume")
    """Sube el volumen del sistema en un porcentaje determinado."""
    
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = min(100, volumen_actual + incremento)  # Máximo 100%
    
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    update_response_with_delay(f"Volumen aumentado a {int(nuevo_volumen)}%")

def bajar_volumen(decremento=10):
    db_logger.log_question(f"bajar volume")
    """Baja el volumen del sistema en un porcentaje determinado."""
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = max(0, volumen_actual - decremento)  # Mínimo 0%
    
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    update_response_with_delay(f"Volumen reducido a {int(nuevo_volumen)}%")
#COntrolar brillo
def ajustar_brillo(porcentaje):
    """Ajusta el brillo de la pantalla al porcentaje indicado (0-100)."""
    try:
        sbc.set_brightness(porcentaje)
        update_response_with_delay(f"Brillo ajustado a {porcentaje}%")
    except Exception as e:
        update_response_with_delay("No se pudo cambiar el brillo.")
        print(f"Error al ajustar brillo: {e}")

def subir_brillo(incremento=10):
    db_logger.log_question(f"subir  brillo")
    """Aumenta el brillo de la pantalla en el porcentaje indicado."""
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]  # Obtener brillo actual
        nuevo_brillo = min(100, brillo_actual + incremento)  # Máximo 100%
        sbc.set_brightness(nuevo_brillo)
        update_response_with_delay(f"Brillo aumentado a {nuevo_brillo}%")
    except Exception as e:
        update_response_with_delay("No se pudo aumentar el brillo.")
        print(f"Error al subir brillo: {e}")

def bajar_brillo(decremento=10):
    db_logger.log_question(f"bajar brillo")
    """Disminuye el brillo de la pantalla en el porcentaje indicado."""
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]
        nuevo_brillo = max(0, brillo_actual - decremento)  # Mínimo 0%
        sbc.set_brightness(nuevo_brillo)
        update_response_with_delay(f"Brillo reducido a {nuevo_brillo}%")
    except Exception as e:
        update_response_with_delay("No se pudo reducir el brillo.")
        print(f"Error al bajar brillo: {e}")

# Controlar música
def controlar_musica(comando):
    """Ejecuta comandos de música en Spotify."""
   
    try:
        if "pausa" in comando:
            db_logger.log_question(f"pausar spotify")
            spotify.pause_playback()
            update_response_with_delay("Música pausada")
        elif "reproducir" in comando:
            db_logger.log_question(f"reproducir spotify")
            spotify.start_playback()
            update_response_with_delay("Reproduciendo música")
        elif "siguiente" in comando:
            db_logger.log_question(f"siguiente cancion")
            spotify.next_track()
            update_response_with_delay("Siguiente canción")
        elif "anterior" in comando: 
            db_logger.log_question(f"anterior cancion")
            spotify.previous_track()
            update_response_with_delay("Canción anterior")

        elif "qué suena" in comando:
            db_logger.log_question(f"Que suena ")
            track_info = spotify.get_current_track()
            if track_info:
                nombre_cancion = track_info.split("]")[-1].strip()
                update_response_with_delay(f" {nombre_cancion}")
            else:
                update_response_with_delay("No se pudo obtener la información de la canción.")
    except Exception as e:
        update_response_with_delay("Hubo un problema con Spotify. Verifica que la aplicación esté abierta y que un dispositivo esté activo.")
        print(f"Error en controlar_musica: {e}")

def extraer_categoria(comando):
    """Extrae la categoría del comando."""
    
    # Lista de palabras clave para categorías
    palabras_categorias = ["miedo", "programación", "chiste negro", "navidad", "raro","raros"]
    
    # Buscar la categoría en el comando
    for palabra in palabras_categorias:
        if palabra in comando.lower():
            return palabra
    
    # Si no se encuentra ninguna categoría, devolver "chiste" como valor predeterminado
    return "chiste"


# Función para ejecutar comandos

def ejecutar_comando(comando):
    """Procesa el comando de voz y ejecuta la acción correspondiente."""
    eel.updateText(f"Has dicho: {comando}")
    
    if any(frase in comando for frase in ["preguntas frecuentes", "preguntas más comunes", "sugerencias comunes", "cosas más preguntadas"]):
        responder_preguntas_frecuentes()
        return

    if any(frase in comando for frase in ["preguntas menos frecuentes", "menos preguntadas", "preguntas raras", "lo menos común"]):
        responder_preguntas_menos_frecuentes()
        return


    if "reproduce" in comando or "pon" in comando:
        song_name = comando.replace("reproduce", "").replace("pon", "").strip()
        if song_name:
            try:
                respuesta = spotify.start_playback(song_name)
                update_response_with_delay(respuesta)
            except Exception as e:
                update_response_with_delay("Error al reproducir la canción. Verifica si tienes un dispositivo activo en Spotify.")
                print(f"Error en reproducir canción: {e}")
        else:
            update_response_with_delay("No entendí qué canción quieres reproducir.")
        return

    if "cerrar" in comando:
        nombre_app = comando.replace("cerrar", "").strip()
        cerrar_aplicacion(nombre_app)
        return

    if "abrir" in comando:
        nombre_app = comando.replace("abrir", "").strip()
        abrir_aplicacion(nombre_app)
        return
    
    if "subir volumen" in comando:
        subir_volumen()
        return

    if "bajar volumen" in comando:
        bajar_volumen()
        return
    
    if "subir brillo" in comando:
        subir_brillo()
        return

    if "bajar brillo" in comando:
        bajar_brillo()
        return

    if any(palabra in comando for palabra in ["volumen", "brillo"]):
        ajustar_nivel(comando)
        return
    
    if any(palabra in comando for palabra in ["chiste", "cuéntame un chiste", "dime un chiste", "cuenta un chiste"]):
        # Extraer la categoría del comando
        db_logger.log_question(f"contar un chiste")
        categoria = extraer_categoria(comando)
        contar_chiste(categoria)
        return
    
    # Comando para "clima mañana" o "pronóstico mañana"
    if "clima" in comando and "mañana" in comando:
        # Limpiar el comando para extraer la ciudad correctamente
        ciudad = comando.replace("clima", "").replace("mañana", "").replace("pronóstico", "").strip()

        # Revisar si se ha extraído una ciudad
        if ciudad:
            print(f"Ciudad extraída: {ciudad}")  # Para depuración, mostrar la ciudad extraída
            pronostico_ciudad_comando(ciudad, 1)  # Obtener pronóstico para 1 día (mañana)
        else:
            print("No se pudo extraer la ciudad.")  # Para depuración
            pronostico_comando(days=1)  # Pronóstico para 1 día con ciudad predeterminada
        return

    # Comando para "cuál es el clima en X ciudad"
    if "cuál es el clima en" in comando:
        db_logger.log_question(f"cual es el cliama en ")
        ciudad = comando.replace("cuál es el clima en", "").strip()
        clima_ciudad_comando(ciudad)
        return

    # Comando para "clima hoy" o "pronóstico para X ciudad"
    if "cual es" in comando and "clima" in comando:
        ciudad = comando.replace("cual es", "").replace("clima", "").strip()
        clima_ciudad_comando(ciudad)  # Clima de una ciudad específica
        return
        
    if "clima" in comando:
        if "hoy" in comando:
            clima_comando()  # Obtiene el clima hoy de la ciudad predeterminada
        else:
            ciudad = comando.replace("clima", "").strip()
            clima_ciudad_comando(ciudad)
        return

    if "pronóstico" in comando:
        if "para" in comando:
            ciudad = comando.split("para")[-1].strip()
            pronostico_ciudad_comando(ciudad)  # Pronóstico para una ciudad específica
        else:
            pronostico_comando()  # Pronóstico de los próximos días para la ciudad predeterminada
        return
    

    controlar_musica(comando)
