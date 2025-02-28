import threading
import eel
import pyautogui
from flask import Flask
from modules.speech import reconocer_voz
from modules.commands import ejecutar_comando

# Inicializar Eel
eel.init('web')

# Inicializar Flask para API
app = Flask(__name__)

@eel.expose
def start_listening():
    """Iniciar el reconocimiento de voz en un hilo separado."""
    threading.Thread(target=reconocer_voz, args=(ejecutar_comando,), daemon=True).start()

def run_flask():
    """Ejecutar Flask en un hilo separado."""
    app.run(port=8080, debug=False, use_reloader=False)

if __name__ == "__main__":
    try:
        # Ejecutar Flask en un hilo separado
        threading.Thread(target=run_flask, daemon=True).start()

        # Obtener tamaño de pantalla
        screen_width, screen_height = pyautogui.size()
        win_width, win_height = 500, 700
        pos_x = (screen_width - win_width) // 2
        pos_y = (screen_height - win_height) // 2

        # Iniciar Eel con la ventana centrada
        eel.start("index.html", mode="chrome", size=(win_width, win_height), position=(pos_x, pos_y))
    except KeyboardInterrupt:
        print("\nPrograma terminado.")
