from modules import db_logger
from modules.commands.sistema import ajustar_nivel, subir_volumen, bajar_volumen, subir_brillo, bajar_brillo
from modules.commands.aplicaciones import abrir_aplicacion, cerrar_aplicacion
from modules.commands.humor import contar_chiste, extraer_categoria
from modules.commands.clima import clima_comando, clima_ciudad_comando, pronostico_comando, pronostico_ciudad_comando
from modules.commands.musica import controlar_musica, spotify
from modules.commands.comunes  import responder_preguntas_frecuentes, update_response_with_delay,responder_preguntas_menos_frecuentes
import eel
from modules.llm import obtener_respuesta_ia,obtener_intencion


# Función para ejecutar comandos
def ejecutar_comando(comando):
    eel.updateText(f"Has dicho: {comando}")
    
    intencion, entidad = obtener_intencion(comando)

    match intencion:
        case "abrir_app":
            db_logger.log_question("abrir_app")
            abrir_aplicacion(entidad)
        case "cerrar_app":
            db_logger.log_question("cerrar_app")
            cerrar_aplicacion(entidad)
        case "reproducir_musica":
            respuesta = spotify.start_playback(entidad or "")
            update_response_with_delay(respuesta)
        case "volumen" | "brillo":
            ajustar_nivel(comando)
        case "clima":
            if "mañana" in comando:
                db_logger.log_question("clima_mañana")
                pronostico_ciudad_comando(entidad or "", 1)
            else:
                db_logger.log_question("clima_hoy")
                clima_ciudad_comando(entidad or "")
        case "chiste":
            contar_chiste(extraer_categoria(comando))
        case "preguntas":
            if intencion == "preguntas_frecuentes":
                responder_preguntas_frecuentes()
            elif intencion == "preguntas_menos_frecuentes":
             responder_preguntas_menos_frecuentes()
        case "pregunta_ia":
            respuesta_ia = obtener_respuesta_ia(comando)
            eel.updateResponse(respuesta_ia)
        case _:
            respuesta_ia = obtener_respuesta_ia(comando)
            eel.updateResponse(respuesta_ia)

