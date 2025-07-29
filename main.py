from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from config import BOT_TOKEN
from handlers import register_handlers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

register_handlers(dp)

if name == "main":
    executor.start_polling(dp, skip_updates=True)
