from argparse import Action
from random import random
from tkinter import Text
from typing import Dict, List, Any

from google.auth.transport import requests
from rasa_sdk import Tracker, logger
from rasa_sdk.executor import CollectingDispatcher


class WeatherHandler:
    """Обработчик погодных запросов"""
    API_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_weather(self, location: str) -> Dict:
        """Получение данных о погоде"""
        try:
            response = requests.get(
                self.API_URL,
                params={
                    'q': location,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'ru'
                },
                timeout=8
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None


class WeatherAction(Action):
    def __init__(self):
        self.weather_service = WeatherHandler("c4aec831b9f8a6d4a4acc553848b76ff")

    def name(self) -> Text:
        return "weather_query_action"

    def compose_response(self, data: Dict, city: str) -> str:
        """Формирование ответа с погодой"""
        conditions = data['weather'][0]['description']
        temp = data['main']['temp']
        details = {
            'влажность': f"{data['main']['humidity']}%",
            'давление': f"{data['main']['pressure']} гПа",
            'ветер': f"{data['wind']['speed']} м/с"
        }

        templates = [
            f"В {city} сейчас {conditions}, температура {temp}°C. Дополнительно: {', '.join(f'{k}: {v}' for k, v in details.items())}",
            f"Погода в {city}: {conditions}, {temp}°C. Параметры: {', '.join(f'{k} {v}' for k, v in details.items())}",
            f"Сейчас в {city}: {conditions}, {temp} градусов. {', '.join(f'{k} - {v}' for k, v in details.items())}"
        ]

        return random.choice(templates)

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message("Укажите город для проверки погоды")
            return []

        weather_data = self.weather_service.fetch_weather(location)

        if not weather_data or weather_data.get('cod') != 200:
            dispatcher.utter_message("Не удалось получить данные. Проверьте название города.")
            return []

        response = self.compose_response(weather_data, location)
        dispatcher.utter_message(response)

        return [SlotSet("location", None)]
