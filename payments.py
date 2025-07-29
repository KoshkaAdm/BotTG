from aiogram.types import LabeledPrice
from datetime import datetime, timedelta

PROVIDER_TOKEN = "test_8Drr3cPY2gkjsWM2jWJK8wJF_Mj5nxADqtRvWo8NolQ"
PAYMENT_TITLE = "Подписка на 30 дней"
PAYMENT_DESCRIPTION = "Снятие лимитов и полный доступ к функциям бота"

PRICE_RUBLES = 29900  # копейки

price = [LabeledPrice(label="Подписка на месяц", amount=PRICE_RUBLES)]

def get_subscription_expiry():
    return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
