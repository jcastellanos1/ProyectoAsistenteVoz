
from modules.commands.sistema import ajustar_nivel
from modules.commands.aplicaciones import abrir_aplicacion, cerrar_aplicacion
from modules.commands.humor import contar_chiste, extraer_categoria
from modules.commands.clima import clima_ciudad_comando, pronostico_ciudad_comando
from modules.commands.musica import controlar_musica, spotify
from modules.commands.comunes import responder_preguntas_frecuentes, update_response_with_delay
import eel
from modules.llm import obtener_respuesta_ia, obtener_intencion

# Lista de entidades reservadas que no deben usarse como nombre de canción
ENTIDADES_CONTROL = ["que_suena", "pausar", "reproducir", "siguiente", "anterior"]

# Función para ejecutar comandos
def ejecutar_comando(comando):
    eel.updateText(f"Has dicho: {comando}")
    intencion, entidad = obtener_intencion(comando)

    match intencion:
        case "abrir_app":
            db_logger.log_question(comando)
            abrir_aplicacion(entidad)
            return f"Abriendo {entidad}"  # 🔄
        case "cerrar_app":
            db_logger.log_question(comando)
            cerrar_aplicacion(entidad)
            return f"Cerrando {entidad}"  # 🔄
        case "reproducir_musica":
            if entidad and entidad.lower() not in ENTIDADES_CONTROL:
                respuesta = spotify.start_playback(entidad)
                update_response_with_delay(respuesta)
                return respuesta  # 🔄
            else:
                controlar_musica("reproducir")
                return "Reproduciendo música"  # 🔄
        case "musica_control":
            controlar_musica(entidad)
            return f"Control de música: {entidad}"  # 🔄
        case "volumen" | "brillo":
            ajustar_nivel(comando)
            return "Ajuste aplicado"  # 🔄
        case "clima":
            if "mañana" in comando:
                db_logger.log_question(comando)
                pronostico_ciudad_comando(entidad or "", 1)
                return "Mostrando pronóstico del clima para mañana"  # 🔄
            else:
                db_logger.log_question(comando)
                clima_ciudad_comando(entidad or "")
                return "Mostrando clima actual"  # 🔄
        case "chiste":
            return contar_chiste(extraer_categoria(comando))  # 🔄
        case "pregunta_ia":
            respuesta_ia = obtener_respuesta_ia(comando)
            eel.updateResponse(respuesta_ia)
            return respuesta_ia  # 🔄
        case _:
            respuesta_ia = obtener_respuesta_ia(comando)
            eel.updateResponse(respuesta_ia)
            return respuesta_ia  # 🔄
