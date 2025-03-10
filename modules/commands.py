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
spotify = SpotifyControl()

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

def contar_chiste(categoria):
    """Obtiene un chiste de la categoría especificada y lo muestra."""

    # Convertimos la categoría recibida a minúsculas para hacer la comparación insensible a mayúsculas
    categoria_ingles = categorias.get(categoria.lower(), "Any") 
   
    if categoria_ingles == "Any":
        print("No se encontró categoría válida. Usando 'Any'.")
    
    # Hacemos la solicitud a la API (en inglés)
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
        else:  # Si es un chiste de una sola parte
            chiste = data["joke"]
        
        chiste_traducido = traducir_al_espanol(chiste)
        
        # Actualizar la interfaz o mostrar el chiste
        eel.updateResponse(chiste_traducido)
        return chiste_traducido
    else:
        mensaje_error = f"No pude obtener un chiste de la categoría {categoria}."
        eel.updateResponse(mensaje_error)
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
        eel.updateResponse("No entendí el comando correctamente.")
                           
def clima_comando(city="Santa Lucía Cotzumalguapa, GT"):
    """Comando para obtener el clima actual de una ciudad."""
    print(get_weather(city))  # Muestra el clima actual
    eel.updateResponse(get_weather(city))

def pronostico_comando(city="Santa Lucía Cotzumalguapa, GT", days=3):
    """Comando para obtener el pronóstico de clima para los próximos días."""
    print(get_forecast(city, days))  # Muestra el pronóstico para los próximos días
    eel.updateResponse(get_forecast(city, days))

def clima_ciudad_comando(city):
    """Comando para obtener el clima actual de una ciudad específica."""
    print(get_weather(city))  # Muestra el clima actual de la ciudad especificada
    eel.updateResponse(get_weather(city))

def pronostico_ciudad_comando(city, days=3):
    """Comando para obtener el pronóstico de clima de una ciudad específica."""
    print(get_forecast(city, days))  # Muestra el pronóstico para los próximos días de la ciudad especificada
    eel.updateResponse(get_forecast(city, days))

def convertir_numero(texto):
    """Convierte palabras a números (Ej: 'cincuenta' → 50)."""
    try:
        return w2n.word_to_num(texto)
    except ValueError:
        return None

# Abrir apps
def abrir_aplicacion(nombre):
    """Abre una aplicación o una URL según el diccionario."""
    app = APLICACIONES.get(nombre)
    if app:
        if "exe" in app:
            subprocess.Popen(app["exe"], shell=True)
            eel.updateResponse(f"Abriendo {nombre}...")
        elif "url" in app:
            webbrowser.open(app["url"])
            eel.updateResponse(f"Reproduciendo {nombre}...")
    else:
        eel.updateResponse(f"No tengo registrado {nombre}.")

# Cerrar apps
def cerrar_aplicacion(nombre):
    """Cierra una aplicación si está en ejecución."""
    app = APLICACIONES.get(nombre)
    if app and "exe" in app:
        proceso_nombre = app["exe"].split("\\")[-1].lower()  # Extraer solo el nombre del ejecutable en minúsculas
        for proceso in psutil.process_iter(attrs=['pid', 'name']):
            if proceso.info['name'].lower() == proceso_nombre:
                psutil.Process(proceso.info['pid']).terminate()
                eel.updateResponse(f"Cerrando {nombre}...")
                return
        eel.updateResponse(f"{nombre} no está en ejecución.")
    else:
        eel.updateResponse(f"No puedo cerrar {nombre}.")

# COntrol volumen
def ajustar_volumen(porcentaje):
    """Ajusta el volumen del sistema al porcentaje especificado (0-100)."""
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    # Normalizar el volumen al rango entre 0.0 y 1.0
    volumen.SetMasterVolumeLevelScalar(porcentaje / 100, None)
    eel.updateResponse(f"Volumen ajustado a {porcentaje}%")

def subir_volumen(incremento=10):
    """Sube el volumen del sistema en un porcentaje determinado."""
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = min(100, volumen_actual + incremento)  # Máximo 100%
    
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    eel.updateResponse(f"Volumen aumentado a {int(nuevo_volumen)}%")

def bajar_volumen(decremento=10):
    """Baja el volumen del sistema en un porcentaje determinado."""
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = max(0, volumen_actual - decremento)  # Mínimo 0%
    
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    eel.updateResponse(f"Volumen reducido a {int(nuevo_volumen)}%")
#COntrolar brillo
def ajustar_brillo(porcentaje):
    """Ajusta el brillo de la pantalla al porcentaje indicado (0-100)."""
    try:
        sbc.set_brightness(porcentaje)
        eel.updateResponse(f"Brillo ajustado a {porcentaje}%")
    except Exception as e:
        eel.updateResponse("No se pudo cambiar el brillo.")
        print(f"Error al ajustar brillo: {e}")

def subir_brillo(incremento=10):
    """Aumenta el brillo de la pantalla en el porcentaje indicado."""
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]  # Obtener brillo actual
        nuevo_brillo = min(100, brillo_actual + incremento)  # Máximo 100%
        sbc.set_brightness(nuevo_brillo)
        eel.updateResponse(f"Brillo aumentado a {nuevo_brillo}%")
    except Exception as e:
        eel.updateResponse("No se pudo aumentar el brillo.")
        print(f"Error al subir brillo: {e}")

def bajar_brillo(decremento=10):
    """Disminuye el brillo de la pantalla en el porcentaje indicado."""
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]
        nuevo_brillo = max(0, brillo_actual - decremento)  # Mínimo 0%
        sbc.set_brightness(nuevo_brillo)
        eel.updateResponse(f"Brillo reducido a {nuevo_brillo}%")
    except Exception as e:
        eel.updateResponse("No se pudo reducir el brillo.")
        print(f"Error al bajar brillo: {e}")

# Controlar música
def controlar_musica(comando):
    """Ejecuta comandos de música en Spotify."""
    try:
        if "pausa" in comando:
            spotify.pause_playback()
            eel.updateResponse("Música pausada")
        elif "reproducir" in comando:
            spotify.start_playback()
            eel.updateResponse("Reproduciendo música")
        elif "siguiente" in comando:
            spotify.next_track()
            eel.updateResponse("Siguiente canción")
        elif "anterior" in comando:
            spotify.previous_track()
            eel.updateResponse("Canción anterior")
        elif "volumen" in comando:
            palabras = comando.split()
            numeros = [convertir_numero(word) for word in palabras if convertir_numero(word) is not None]
            if numeros:
                vol = numeros[0]
                spotify.set_volume(vol)
                eel.updateResponse(f"Volumen ajustado a {vol}%")
            else:
                eel.updateResponse("No entendí el nivel de volumen.")
        elif "que suena" in comando:
            track_info = spotify.get_current_track()
            if track_info:
                nombre_cancion = track_info.split("]")[-1].strip()
                eel.updateResponse(f" {nombre_cancion}")
            else:
                eel.updateResponse("No se pudo obtener la información de la canción.")
    except Exception as e:
        eel.updateResponse("Hubo un problema con Spotify. Verifica que la aplicación esté abierta y que un dispositivo esté activo.")
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

    if "reproduce" in comando or "pon" in comando:
        song_name = comando.replace("reproduce", "").replace("pon", "").strip()
        if song_name:
            try:
                respuesta = spotify.start_playback(song_name)
                eel.updateResponse(respuesta)
            except Exception as e:
                eel.updateResponse("Error al reproducir la canción. Verifica si tienes un dispositivo activo en Spotify.")
                print(f"Error en reproducir canción: {e}")
        else:
            eel.updateResponse("No entendí qué canción quieres reproducir.")
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
