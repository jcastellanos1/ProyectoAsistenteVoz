import subprocess
import webbrowser
import psutil
from modules.commands.comunes import update_response_with_delay
from modules import db_logger

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

def abrir_aplicacion(nombre):
    db_logger.log_question(f"abrir aplicacion: {nombre}")
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

def cerrar_aplicacion(nombre):
    db_logger.log_question(f"cerrar aplicacion: {nombre}")
    app = APLICACIONES.get(nombre)
    if app and "exe" in app:
        proceso_nombre = app["exe"].split("\\")[-1].lower()
        for proceso in psutil.process_iter(attrs=['pid', 'name']):
            if proceso.info['name'].lower() == proceso_nombre:
                psutil.Process(proceso.info['pid']).terminate()
                update_response_with_delay(f"Cerrando {nombre}...")
                return
        update_response_with_delay(f"{nombre} no está en ejecución.")
    else:
        update_response_with_delay(f"No puedo cerrar {nombre}.")
