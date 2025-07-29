from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Command
from openai_client import generate_text
from database import get_usage, increment_usage, is_subscribed
from payments import price, PROVIDER_TOKEN, get_subscription_expiry
from database import activate_subscription
from sheets_client import create_user_sheet, append_expense, append_task

dp = Dispatcher()

FREE_LIMIT = 10

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer("РџСЂРёРІРµС‚! РЇ Р±РѕС‚ В«РўРѕ С‡С‚Рѕ РЅР°РґРѕВ» рџ‘‹\n\nР“РµРЅРµСЂРёСЂСѓСЋ С‚РµРєСЃС‚С‹, С‚Р°Р±Р»РёС†С‹ Рё Р»РѕРіРѕ. РќР°РїРёС€Рё С‚РµРјСѓ, Рё СЏ СЃРѕР·РґР°Рј С‚РµРєСЃС‚!")

@dp.message_handler(lambda msg: msg.text.lower().startswith("Р»РѕРіРѕС‚РёРї "))
async def handle_logo(msg: types.Message):
    from logo_generator import generate_logo
    user_id = msg.from_user.id
    if not is_subscribed(user_id) and get_usage(user_id) >= FREE_LIMIT:
        await msg.answer("вљ пёЏ Р›РёРјРёС‚ Р±РµСЃРїР»Р°С‚РЅС‹С… РіРµРЅРµСЂР°С†РёР№ Р»РѕРіРѕС‚РёРїРѕРІ РёСЃС‡РµСЂРїР°РЅ. РћС„РѕСЂРјРё РїРѕРґРїРёСЃРєСѓ.")
        return
    prompt = msg.text[8:].strip()
    await msg.answer("рџЋЁ Р“РµРЅРµСЂРёСЂСѓСЋ Р»РѕРіРѕС‚РёРї...")
    url = await generate_logo(prompt)
    if url.startswith("http"):
        await msg.answer_photo(url, caption="Р’РѕС‚ Р»РѕРіРѕС‚РёРї!")
    else:
        await msg.answer(url)
    increment_usage(user_id)

@dp.message_handler(commands=["create_table"])
async def create_table(msg: types.Message):
    url = create_user_sheet(msg.from_user.id)
    await msg.answer(f"вњ… РўР°Р±Р»РёС†Р° СЃРѕР·РґР°РЅР°: {url}")

@dp.message_handler(commands=["sheet_link"])
async def get_sheet_link(msg: types.Message):
    try:
        url = f"https://docs.google.com/spreadsheets/d/UserSheet_{msg.from_user.id}"
        await msg.answer(f"рџ“Ћ Р’Р°С€Р° С‚Р°Р±Р»РёС†Р°: {url}")
    except:
        await msg.answer("вљ пёЏ РўР°Р±Р»РёС†Р° РїРѕРєР° РЅРµ СЃРѕР·РґР°РЅР°. РСЃРїРѕР»СЊР·СѓР№ /create_table")

@dp.message_handler(commands=["add_expense"])
async def add_expense_cmd(msg: types.Message):
    try:
        parts = msg.text.split(maxsplit=2)
        amount = parts[1]
        category = parts[2]
        append_expense(msg.from_user.id, amount, category)
        await msg.answer("рџ’ё Р Р°СЃС…РѕРґ РґРѕР±Р°РІР»РµРЅ РІ С‚Р°Р±Р»РёС†Сѓ.")
    except:
        await msg.answer("вљ пёЏ Р¤РѕСЂРјР°С‚: /add_expense 500 РњР°СЂРєРµС‚РёРЅРі")

@dp.message_handler(commands=["add_task"])
async def add_task_cmd(msg: types.Message):
    try:
        task = msg.text.split(maxsplit=1)[1]
        append_task(msg.from_user.id, task)
        await msg.answer("рџ“Њ Р—Р°РґР°С‡Р° РґРѕР±Р°РІР»РµРЅР° РІ С‚Р°Р±Р»РёС†Сѓ.")
    except:
        await msg.answer("вљ пёЏ Р¤РѕСЂРјР°С‚: /add_task РЎРґРµР»Р°С‚СЊ Р»РµРЅРґРёРЅРі")

@dp.message_handler(commands=["buy"])
async def buy_cmd(msg: types.Message):
    await msg.answer_invoice(
        title="РџРѕРґРїРёСЃРєР° РЅР° Р±РѕС‚Р°",
        description="РЎРЅСЏС‚РёРµ Р»РёРјРёС‚РѕРІ Рё РїРѕР»РЅС‹Р№ РґРѕСЃС‚СѓРї РЅР° 30 РґРЅРµР№",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=price,
        start_parameter="subscribe-bot",
        payload="subscription"
    )

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(pre_checkout_q: types.PreCheckoutQuery):
    await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(msg: types.Message):
    expiry = get_subscription_expiry()
    activate_subscription(msg.from_user.id, expiry)
    await msg.answer(f"вњ… РџРѕРґРїРёСЃРєР° Р°РєС‚РёРІРёСЂРѕРІР°РЅР° РґРѕ {expiry}!
РЎРїР°СЃРёР±Рѕ Р·Р° РѕРїР»Р°С‚Сѓ рџ’™")

@dp.message_handler(commands=["check"])
async def check_subscription(msg: types.Message):
    if is_subscribed(msg.from_user.id):
        await msg.answer("вњ… РЈ С‚РµР±СЏ Р°РєС‚РёРІРЅР°СЏ РїРѕРґРїРёСЃРєР°!")
    else:
        await msg.answer("рџљ« РџРѕРґРїРёСЃРєР° РЅРµ РЅР°Р№РґРµРЅР° РёР»Рё РёСЃС‚РµРєР»Р°.")

@dp.message_handler()
async def handle_prompt(msg: types.Message):
    user_id = msg.from_user.id
    if not is_subscribed(user_id) and get_usage(user_id) >= FREE_LIMIT:
        await msg.answer("вљ пёЏ РўС‹ РёСЃС‡РµСЂРїР°Р» Р»РёРјРёС‚ Р±РµСЃРїР»Р°С‚РЅС‹С… РіРµРЅРµСЂР°С†РёР№.\nРћС„РѕСЂРјРё РїРѕРґРїРёСЃРєСѓ, С‡С‚РѕР±С‹ РїСЂРѕРґРѕР»Р¶РёС‚СЊ.")
        return
    await msg.answer("вњЌ Р“РµРЅРµСЂРёСЂСѓСЋ С‚РµРєСЃС‚...")
    reply = await generate_text(msg.text)
    await msg.answer(reply)
    increment_usage(user_id)
