from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from config import BOT_TOKEN
from handlers import dp

bot = Bot(token=BOT_TOKEN)
dp.bot = bot

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
