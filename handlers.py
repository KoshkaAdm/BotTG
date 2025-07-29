from aiogram import Router, types
from aiogram.filters import Command
from openai_client import generate_text
from database import get_usage, increment_usage

router = Router()
FREE_LIMIT = 10

@router.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer("Привет! Я бот «То что надо» 👋\n\nГенерирую тексты, таблицы и лого. Напиши тему, и я создам текст!")

@router.message()
async def handle_prompt(msg: types.Message):
    user_id = msg.from_user.id
    usage = get_usage(user_id)

    if usage >= FREE_LIMIT:
        await msg.answer("⚠️ Ты исчерпал лимит бесплатных генераций.\nОформи подписку, чтобы продолжить.")
        return

    await msg.answer("✍ Генерирую текст...")
    reply = await generate_text(msg.text)
    await msg.answer(reply)
    increment_usage(user_id)


@router.message(Command("logo"))
async def logo_cmd(msg: types.Message):
    await msg.answer("🖌 Напиши, что должно быть на логотипе (например: «логотип кофейни с чашкой и паром»)")

@router.message(lambda m: m.text.lower().startswith("логотип "))
async def handle_logo(msg: types.Message):
    from logo_generator import generate_logo
    user_id = msg.from_user.id
    usage = get_usage(user_id)

    if usage >= FREE_LIMIT:
        await msg.answer("⚠️ Лимит бесплатных генераций логотипов исчерпан. Оформи подписку.")
        return

    prompt = msg.text[8:].strip()
    await msg.answer("🎨 Генерирую логотип...")
    url = await generate_logo(prompt)
    if url.startswith("http"):
        await msg.answer_photo(url, caption="Вот логотип!")
    else:
        await msg.answer(url)
    increment_usage(user_id)


from sheets_client import create_user_sheet, append_expense, append_task

@router.message(Command("create_table"))
async def create_table(msg: types.Message):
    url = create_user_sheet(msg.from_user.id)
    await msg.answer(f"✅ Таблица создана: {url}")

@router.message(Command("sheet_link"))
async def get_sheet_link(msg: types.Message):
    try:
        url = f"https://docs.google.com/spreadsheets/d/UserSheet_{msg.from_user.id}"
        await msg.answer(f"📎 Ваша таблица: {url}")
    except:
        await msg.answer("⚠️ Таблица пока не создана. Используй /create_table")

@router.message(Command("add_expense"))
async def add_expense_cmd(msg: types.Message):
    try:
        parts = msg.text.split(maxsplit=2)
        amount = parts[1]
        category = parts[2]
        append_expense(msg.from_user.id, amount, category)
        await msg.answer("💸 Расход добавлен в таблицу.")
    except:
        await msg.answer("⚠️ Формат: /add_expense 500 Маркетинг")

@router.message(Command("add_task"))
async def add_task_cmd(msg: types.Message):
    try:
        task = msg.text.split(maxsplit=1)[1]
        append_task(msg.from_user.id, task)
        await msg.answer("📌 Задача добавлена в таблицу.")
    except:
        await msg.answer("⚠️ Формат: /add_task Сделать лендинг")

from aiogram import types
from aiogram.filters import Command
from payments import price, PROVIDER_TOKEN, get_subscription_expiry
from database import activate_subscription, is_subscribed

@router.message(Command("buy"))
async def buy_cmd(msg: types.Message):
    await msg.answer_invoice(
        title="Подписка на бота",
        description="Снятие лимитов и полный доступ на 30 дней",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=price,
        start_parameter="subscribe-bot",
        payload="subscription"
    )

@router.pre_checkout_query()
async def checkout(pre_checkout_q: types.PreCheckoutQuery, bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@router.message(lambda msg: msg.successful_payment is not None)
async def successful_payment(msg: types.Message):
    expiry = get_subscription_expiry()
    activate_subscription(msg.from_user.id, expiry)
    await msg.answer(f"✅ Подписка активирована до {expiry}! Спасибо за оплату 💙")

@router.message(Command("check"))
async def check_subscription(msg: types.Message):
    if is_subscribed(msg.from_user.id):
        await msg.answer("✅ У тебя активная подписка!")
    else:
        await msg.answer("🚫 Подписка не найдена или истекла.")
