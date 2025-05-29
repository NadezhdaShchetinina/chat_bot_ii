import webbrowser
from argparse import Action
from datetime import datetime
from pipes import quote
from random import random
from tkinter import Text
from typing import Dict, Any, List

from rasa_sdk import Tracker, logger
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher




def name() -> str:
    return "action_get_time"


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

class ActionCalculate(Action):
    def name(self) -> str:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> list[Any] | list[dict[str, Any]]:

        expression = tracker.get_slot("expression")
        if not expression:
            dispatcher.utter_message(text="Пожалуйста, введите выражение для вычисления.")
            return []

        try:
            expression = expression.replace('x', '*')
            result = eval(expression)
            dispatcher.utter_message(text=f"Результат: {result}")
        except (SyntaxError, TypeError, NameError, ZeroDivisionError):
            dispatcher.utter_message(text="Не могу вычислить это выражение.")

        return [SlotSet("expression", None)]


class ActionAnalyzeMood(Action):
    def name(self) -> str:
        return "action_analyze_mood"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "").lower()

        positive_words = ["хорошо", "отлично", "прекрасно", "радость", "счастлив", "ура", "люблю", "классно",
                          "замечательно"]
        negative_words = ["плохо", "ужасно", "грустно", "несчастье", "тоскливо", "разочарован", "устал", "бесит"]

        positive_count = sum(word in user_message for word in positive_words)
        negative_count = sum(word in user_message for word in negative_words)

        if positive_count > negative_count:
            mood = "positive"
        elif negative_count > positive_count:
            mood = "negative"
        else:
            mood = "neutral"

        responses = {
            "positive": [
                "Ты звучишь очень позитивно! 😄 Чем могу порадовать тебя ещё?",
                "Похоже, у вас отличное настроение!",
                "Я чувствую вашу радость! Так держать!"
            ],
            "negative": [
                "Ты, похоже, не в настроении... 😔 Хочешь поговорить об этом?",
                "Кажется, вам сейчас нелегко...",
                "Ваше настроение кажется подавленным. Если нужно поговорить - я здесь."
            ],
            "neutral": [
                "Улавливаю нейтральный настрой. Спрашивай, если что-нибудь нужно!",
                "Ваше настроение кажется ровным. Все в порядке?",
                "Похоже, у вас обычный день. Надеюсь, он станет еще лучше!"
            ]
        }

        dispatcher.utter_message(text=random.choice(responses[mood]))
        return []
