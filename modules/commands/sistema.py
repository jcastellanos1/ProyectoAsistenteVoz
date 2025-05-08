
import re
from modules.commands.comunes import update_response_with_delay
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
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
    db_logger.log_question("subir volume")
    """Sube el volumen del sistema en un porcentaje determinado."""
    
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = min(100, volumen_actual + incremento)  # Máximo 100%
    
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    update_response_with_delay(f"Volumen aumentado a {int(nuevo_volumen)}%")

def bajar_volumen(decremento=10):
    db_logger.log_question("bajar volume")
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
    db_logger.log_question("subir  brillo")
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
    db_logger.log_question("bajar brillo")
    """Disminuye el brillo de la pantalla en el porcentaje indicado."""
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]
        nuevo_brillo = max(0, brillo_actual - decremento)  # Mínimo 0%
        sbc.set_brightness(nuevo_brillo)
        update_response_with_delay(f"Brillo reducido a {nuevo_brillo}%")
    except Exception as e:
        update_response_with_delay("No se pudo reducir el brillo.")
        print(f"Error al bajar brillo: {e}")

