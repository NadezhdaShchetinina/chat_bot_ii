from datetime import datetime
import random
import requests
import webbrowser
from urllib.parse import quote
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


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
        self.weather_service = WeatherHandler("a83e1039a7cd83d057821e4fe86591e6")

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


class TimeDateAction(Action):
    def name(self) -> Text:
        return "time_info_action"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        current = datetime.now()
        time_format = "%H:%M"
        date_format = "%d %B %Y"

        responses = [
            f"Текущее время: {current.strftime(time_format)}, дата: {current.strftime(date_format)}",
            f"Сейчас {current.strftime(time_format)}, сегодня {current.strftime(date_format)}",
            f"Время: {current.strftime(time_format)}, {current.strftime(date_format)}"
        ]

        dispatcher.utter_message(random.choice(responses))
        return []


class WebSearchAction(Action):
    def name(self) -> Text:
        return "web_search_action"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        search_term = tracker.get_slot("search_term")
        if not search_term:
            dispatcher.utter_message("Укажите, что нужно найти")
            return []

        search_url = f"https://yandex.ru/search/?text={quote(search_term)}"
        webbrowser.open(search_url)

        confirmations = [
            f"Поиск по запросу '{search_term}' выполнен",
            f"Ищу информацию о '{search_term}'",
            f"Результаты по запросу '{search_term}'"
        ]

        dispatcher.utter_message(random.choice(confirmations))
        return []


class EmotionAnalysisAction(Action):
    EMOTION_WORDS = {
        'positive': ['радость', 'счастье', 'восторг', 'удовольствие', 'восхищение'],
        'negative': ['грусть', 'печаль', 'злость', 'разочарование', 'тоска']
    }

    def name(self) -> Text:
        return "emotion_analysis_action"

    def analyze_text(self, text: str) -> str:
        text_lower = text.lower()
        positive = sum(word in text_lower for word in self.EMOTION_WORDS['positive'])
        negative = sum(word in text_lower for word in self.EMOTION_WORDS['negative'])

        if positive > negative:
            return 'positive'
        elif negative > positive:
            return 'negative'
        return 'neutral'

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        user_text = tracker.latest_message.get('text', '')
        mood = self.analyze_text(user_text)

        responses = {
            'positive': [
                "Вы излучаете позитив! 😊",
                "Отличное настроение! Продолжайте в том же духе!",
                "Ваша радость заразительна! 😄"
            ],
            'negative': [
                "Кажется, вам нужна поддержка... 😔",
                "Я здесь, если хотите поговорить об этом.",
                "Тяжелые времена проходят, держитесь! 🤗"
            ],
            'neutral': [
                "Нейтральный тон. Хотите обсудить что-то конкретное?",
                "Спокойный настрой. Чем могу помочь?",
                "Все ровно. Есть вопросы?"
            ]
        }

        dispatcher.utter_message(random.choice(responses[mood]))
        return []


class MathCalculationAction(Action):
    def name(self) -> Text:
        return "math_calculation_action"

    def safe_calculate(self, expression: str) -> float:

        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Недопустимые символы в выражении")

        try:
            return eval(expression, {'__builtins__': None}, {})
        except:
            raise ValueError("Ошибка вычисления")

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        math_expr = tracker.get_slot("math_expression")
        if not math_expr:
            dispatcher.utter_message("Введите математическое выражение")
            return []

        try:
            result = self.safe_calculate(math_expr)
            dispatcher.utter_message(f"Результат: {result:.2f}")
        except ValueError as e:
            dispatcher.utter_message(str(e))

        return [SlotSet("math_expression", None)]