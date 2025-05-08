from modules.weather import get_weather, get_forecast
from modules.commands.comunes import update_response_with_delay

def clima_comando(city="Santa Lucía Cotzumalguapa, GT"):
    """Comando para obtener el clima actual de una ciudad."""
    update_response_with_delay(get_weather(city))

def pronostico_comando(city="Santa Lucía Cotzumalguapa, GT", days=3):
    """Comando para obtener el pronóstico de clima para los próximos días."""
    update_response_with_delay(get_forecast(city, days))

def clima_ciudad_comando(city):
    """Comando para obtener el clima actual de una ciudad específica."""
    update_response_with_delay(get_weather(city))

def pronostico_ciudad_comando(city, days=3):
    """Comando para obtener el pronóstico de clima de una ciudad específica."""
    update_response_with_delay(get_forecast(city, days))
