import eel
import subprocess
import webbrowser
import psutil  # Para cerrar aplicaciones
from word2number import w2n
from modules.spotify_control import SpotifyControl
from modules.weather import get_weather, get_forecast

spotify = SpotifyControl()

# Diccionario de aplicaciones
APLICACIONES = {
    "calculadora": {"exe": "calc.exe"},
    "bloc de notas": {"exe": "notepad.exe"},
    "explorador": {"exe": "explorer.exe"},
    "cmd": {"exe": "cmd.exe"},
    "spotify": {"exe": "spotify.exe"},
    "epic games": {"exe": r"D:\Epic\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"},
    "navegador": {"exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe"},
    "rola": {"url": "https://www.youtube.com/watch?v=nnrp3drhw0k&t=90"},
    "lobo": {"url": "https://www.youtube.com/watch?v=ckkL7-KPD_E&t=48"},
    "criminal": {"url": "https://www.youtube.com/watch?v=VqEbCxg2bNI&t=80"}
}

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
