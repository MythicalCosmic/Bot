import asyncio
import uvicorn
from fastapi import FastAPI, Request
from config.settings import  PORT, WEBHOOK_MODE
from config.bot_setup import bot, dp
from aiogram.types import Update



if WEBHOOK_MODE:
    app = FastAPI()

    @app.post('/Marketing_by_Malika_bot')
    async def webhook(request: Request):
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}


    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=PORT)

else:
    async def main():
        print('Bot started successfully')
        await dp.start_polling(bot)
       
    if __name__ == "__main__":
        asyncio.run(main())
