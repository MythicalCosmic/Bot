import asyncio
import uvicorn
from fastapi import FastAPI
from config.settings import WEBHOOK_URL, PORT, WEBHOOK_MODE
from config.bot_setup import bot, dp
from contextlib import asynccontextmanager


app = FastAPI()  

if WEBHOOK_MODE:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await bot.set_webhook(WEBHOOK_URL)
        yield

    app = FastAPI(lifespan=lifespan)

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=PORT)

else:
    @app.on_event("startup")
    async def start_polling():
        asyncio.create_task(dp.start_polling(bot))  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
