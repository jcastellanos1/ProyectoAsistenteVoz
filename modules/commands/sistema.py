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

    # Buscar valor en texto (ej. "cincuenta")
    valor = None
    for palabra, numero in VALORES_NIVELES.items():
        if re.search(rf'\b{palabra}\b', comando):
            valor = numero
            break

    # Buscar valor numérico (ej. 80)
    if valor is None:
        match = re.search(r"\b(\d{1,3})\b", comando)
        if match:
            valor = int(match.group(1))

    # Interpretaciones especiales
    if "máximo" in comando:
        valor = 100
    elif "mínimo" in comando or "mute" in comando or "silencio" in comando:
        valor = 0
    elif "medio" in comando:
        valor = 50

    # Ejecutar lógica
    if tipo and accion:
        if valor is None:
            valor = 10  # valor por defecto
        if tipo == "volumen":
            if accion == "subir":
                subir_volumen(valor)
            else:
                bajar_volumen(valor)
        elif tipo == "brillo":
            if accion == "subir":
                subir_brillo(valor)
            else:
                bajar_brillo(valor)
    elif tipo and valor is not None:
        # Si hay tipo y valor directo sin acción
        if tipo == "volumen":
            ajustar_volumen(valor)
        elif tipo == "brillo":
            ajustar_brillo(valor)
    else:
        update_response_with_delay("No entendí el comando correctamente.")

# ----------------------------- VOLUMEN -----------------------------

def ajustar_volumen(porcentaje):
    """Ajusta el volumen del sistema al porcentaje especificado (0-100)."""
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    volumen.SetMasterVolumeLevelScalar(porcentaje / 100, None)
    update_response_with_delay(f"Volumen ajustado a {porcentaje}%")

def subir_volumen(incremento=10):
    db_logger.log_question("subir volumen")
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = min(100, volumen_actual + incremento)
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    update_response_with_delay(f"Volumen aumentado a {int(nuevo_volumen)}%")

def bajar_volumen(decremento=10):
    db_logger.log_question("bajar volumen")
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    volumen_actual = volumen.GetMasterVolumeLevelScalar() * 100
    nuevo_volumen = max(0, volumen_actual - decremento)
    volumen.SetMasterVolumeLevelScalar(nuevo_volumen / 100, None)
    update_response_with_delay(f"Volumen reducido a {int(nuevo_volumen)}%")

# ----------------------------- BRILLO -----------------------------

def ajustar_brillo(porcentaje):
    """Ajusta el brillo de la pantalla al porcentaje indicado (0-100)."""
    try:
        sbc.set_brightness(porcentaje)
        update_response_with_delay(f"Brillo ajustado a {porcentaje}%")
    except Exception as e:
        update_response_with_delay("No se pudo cambiar el brillo.")
        print(f"Error al ajustar brillo: {e}")

def subir_brillo(incremento=10):
    db_logger.log_question("subir brillo")
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]
        nuevo_brillo = min(100, brillo_actual + incremento)
        sbc.set_brightness(nuevo_brillo)
        update_response_with_delay(f"Brillo aumentado a {nuevo_brillo}%")
    except Exception as e:
        update_response_with_delay("No se pudo aumentar el brillo.")
        print(f"Error al subir brillo: {e}")

def bajar_brillo(decremento=10):
    db_logger.log_question("bajar brillo")
    try:
        brillo_actual = sbc.get_brightness(display=0)[0]
        nuevo_brillo = max(0, brillo_actual - decremento)
        sbc.set_brightness(nuevo_brillo)
        update_response_with_delay(f"Brillo reducido a {nuevo_brillo}%")
    except Exception as e:
        update_response_with_delay("No se pudo reducir el brillo.")
        print(f"Error al bajar brillo: {e}")
