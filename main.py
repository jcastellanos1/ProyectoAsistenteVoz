import threading
import eel
import pyautogui
from flask import Flask
from modules.speech import reconocer_voz
from modules.speech import set_listening_state
from modules.commands.voice_commands import ejecutar_comando
from modules import db_logger

#incia la BD
db_logger.init_db()


# Inicializar Eel
eel.init('web')

# Inicializar Flask para API
app = Flask(__name__)

from modules.speech import set_listening_state

@eel.expose
def pausar_escucha():
    set_listening_state(False)

@eel.expose
def reanudar_escucha():
    set_listening_state(True)


@eel.expose
def start_listening():
    print("[INFO] start_listening llamado desde JS")  #  DEBUG
    threading.Thread(target=reconocer_voz, args=(ejecutar_comando,), daemon=True).start()

@eel.expose
def simular_comando(texto):
    print(f"[Simulación] Ejecutando pregunta: {texto}")
    return ejecutar_comando(texto)  # Usa tu lógica normal de comandos


@eel.expose
def get_top_questions():
    top = db_logger.obtener_top_preguntas()
    return [{"question": q, "count": c} for q, c in top]

def run_flask():
    """Ejecutar Flask en un hilo separado."""
    app.run(port=8080, debug=False, use_reloader=False)



if __name__ == "__main__":
    try:
        # Ejecutar Flask en un hilo separado
        threading.Thread(target=run_flask, daemon=True).start()

        # Obtener tamaño de pantalla
        screen_width, screen_height = pyautogui.size()
        win_width, win_height = 500, 850
        pos_x = (screen_width - win_width) // 2
        pos_y = (screen_height - win_height) // 2

        # Iniciar Eel con la ventana centrada
        eel.start("index.html", mode="chrome", size=(win_width, win_height), position=(pos_x, pos_y))
    except KeyboardInterrupt:
        print("\nPrograma terminado.")
