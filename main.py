import asyncio
import uvicorn
from fastapi import FastAPI, Request
from aiogram.types import Update
from config.settings import WEBHOOK_MODE, WEBHOOK_URL, PORT
from config.bot_setup import bot, dp
from contextlib import asynccontextmanager

if WEBHOOK_MODE:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await bot.set_webhook(WEBHOOK_URL)
        yield

    app = FastAPI(lifespan=lifespan)
    
    @app.post("/webhook")
    async def receive_update(request: Request):
        try:
            data = await request.json()
            if not data:
                return {"error": "Empty request"}
            update = Update(**data)
            await dp.process_update(update)
        except Exception as e:
            return {"error": str(e)}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=PORT)

else:
    async def main():
        await dp.start_polling(bot)

    if __name__ == "__main__":
        asyncio.run(main())
