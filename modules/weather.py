# weather.py
import locale
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
# Cargar las variables de entorno del archivo .env
load_dotenv()

# Obtener la clave de la API de OpenWeather desde el .env
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"

def get_weather(city):
    """Obtiene el clima actual de una ciudad"""
    try:
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            # Clima actual
            current_weather = data['list'][0]  # El primer resultado es el actual
            temp = current_weather['main']['temp']
            description = current_weather['weather'][0]['description']

            return f"El clima actual en {city} es {temp}°C con {description}."
        else:
            return f"No pude obtener el clima para {city}."
    except Exception as e:
        return f"Hubo un error al obtener los datos: {e}"
    
locale.setlocale(locale.LC_TIME, 'es_GT.UTF-8')  #pone la vaina de la fecha en español

def format_date(date_str):
    """Convierte la fecha de la API a un formato legible (día mes) en español."""
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return date.strftime("%d de %B")  # Esto devuelve la fecha con el mes en español

def get_forecast(city, days=1):
    """Obtiene el pronóstico del clima para los próximos días (incluyendo mañana)"""
    try:
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()

        # Para ver la respuesta de la API
        #print("Respuesta de la API:", data)

        if response.status_code == 200:
            forecast = ""
            # Si es solo para el día siguiente (mañana)
            if days == 1:
                # Encontramos la predicción para mañana
                today = datetime.now().date()
                tomorrow = today + timedelta(days=1)
                print("Hoy es:", today)
                print("Mañana será:", tomorrow)

                # Verificamos la fecha en la respuesta de la API
                for weather in data['list']:
                    date = datetime.strptime(weather['dt_txt'], "%Y-%m-%d %H:%M:%S").date()
                    print("Fecha en la API:", date)
                    if date == tomorrow:
                        temp = weather['main']['temp']
                        description = weather['weather'][0]['description']
                        formatted_date = format_date(weather['dt_txt'])
                        forecast = f"Mañana {formatted_date} el clima en {city} será de {temp}°C con {description}."
                        break
            return forecast if forecast else "No pude obtener el pronóstico para mañana."
        else:
            return f"No pude obtener el pronóstico para {city}."
    except Exception as e:
        return f"Hubo un error al obtener los datos: {e}"

#Pruebas para de formatos
if __name__ == "__main__":
    city = "Santa Lucía Cotzumalguapa, GT"
    print(get_weather(city))  # Clima actual
    print(get_forecast(city, 1))  # Pronóstico para 3 días
