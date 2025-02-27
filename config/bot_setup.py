from aiogram import Bot, Dispatcher
from config.settings import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


from handlers.handlers import router  

dp.include_router(router)
