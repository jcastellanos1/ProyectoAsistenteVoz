from modules.commands.sistema import ajustar_nivel
from modules.commands.aplicaciones import abrir_aplicacion, cerrar_aplicacion
from modules.commands.humor import contar_chiste
from modules.commands.clima import clima_ciudad_comando, pronostico_ciudad_comando
from modules.commands.musica import controlar_musica, spotify
from modules.commands.comunes import responder_preguntas_frecuentes, update_response_with_delay
import eel
from modules.db_logger import log_question
from modules.llm import obtener_respuesta_ia, obtener_intencion

# Lista de entidades reservadas que no deben usarse como nombre de canción
ENTIDADES_CONTROL = ["que_suena", "pausar", "reproducir", "siguiente", "anterior"]

def ejecutar_comando(comando):
    eel.updateText(f"Has dicho: {comando}")
    intencion, entidad = obtener_intencion(comando)

    if not intencion:
        update_response_with_delay("Lo siento, no entendí tu solicitud.")
        return "Comando no reconocido."

    log_question(f"Comando: {comando} | Intención: {intencion} | Entidad: {entidad or 'null'}")

    match intencion:
        case "abrir_app":
            if entidad:
                abrir_aplicacion(entidad)
                return f"Abriendo {entidad}"
            else:
                return "¿Qué aplicación deseas abrir?"

        case "cerrar_app":
            if entidad:
                cerrar_aplicacion(entidad)
                return f"Cerrando {entidad}"
            else:
                return "¿Qué aplicación deseas cerrar?"

        case "reproducir_musica":
            if entidad:
                if entidad.lower() in ENTIDADES_CONTROL:
                    controlar_musica(entidad.lower())
                    return f"Control de música: {entidad}"
                else:
                    respuesta = spotify.start_playback(entidad)
                    update_response_with_delay(respuesta)
                    return respuesta
            else:
                controlar_musica("reproducir")
                return "Reproduciendo música"

        case "musica_control":
            if entidad:
                controlar_musica(entidad.lower())
                return f"Control de música: {entidad}"
            else:
                return "¿Qué acción musical deseas realizar? (pausar, siguiente, etc.)"

        case "volumen":
            ajustar_nivel(comando)
            return "Comando de volumen procesado."

        case "brillo":
            ajustar_nivel(comando)
            return "Comando de brillo procesado."

        case "clima":
            if entidad:
                if "mañana" in comando.lower():
                    pronostico_ciudad_comando(entidad, 1)
                    return f"Mostrando pronóstico para mañana en {entidad}"
                else:
                    clima_ciudad_comando(entidad)
                    return f"Mostrando clima actual en {entidad}"
            else:
                if "mañana" in comando.lower():
                    pronostico_ciudad_comando("", 1)
                    return "Mostrando pronóstico para mañana"
                else:
                    clima_ciudad_comando("")
                    return "Mostrando clima actual"

        case "chiste":
            return contar_chiste(entidad or "chiste")

        case "pregunta_ia":
            respuesta_ia = obtener_respuesta_ia(comando)
            eel.updateResponse(respuesta_ia)
            return respuesta_ia

        case "desconocido" | _:
            respuesta_ia = obtener_respuesta_ia(comando)
            eel.updateResponse(respuesta_ia)
            return respuesta_ia
