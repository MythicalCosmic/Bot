from aiogram import Bot, Dispatcher
from config.settings import TOKEN
from handlers.handlers import router

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)
