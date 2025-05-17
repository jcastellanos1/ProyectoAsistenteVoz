from modules.weather import get_weather, get_forecast
from modules.commands.comunes import update_response_with_delay

CIUDAD_POR_DEFECTO = "Santa Lucía Cotzumalguapa, GT"

def clima_comando(city=None):
    """Comando para obtener el clima actual."""
    ciudad = city if city else CIUDAD_POR_DEFECTO
    try:
        update_response_with_delay(get_weather(ciudad))
    except Exception as e:
        update_response_with_delay(f"No se pudo obtener el clima de {ciudad}.")
        print(f"Error en clima_comando: {e}")

def pronostico_comando(city=None, days=3):
    """Comando para obtener el pronóstico del clima."""
    ciudad = city if city else CIUDAD_POR_DEFECTO
    try:
        update_response_with_delay(get_forecast(ciudad, days))
    except Exception as e:
        update_response_with_delay(f"No se pudo obtener el pronóstico de {ciudad}.")
        print(f"Error en pronostico_comando: {e}")

def clima_ciudad_comando(city):
    """Alias para obtener clima actual."""
    clima_comando(city)

def pronostico_ciudad_comando(city, days=3):
    """Alias para obtener pronóstico."""
    pronostico_comando(city, days)
