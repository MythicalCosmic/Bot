from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from config.settings import get_translation

router = Router()  

@router.message(Command("start"))  
async def say_hi(message: types.Message):
    await message.answer(get_translation('start_message'))


@router.message()
async def fallback_handler(message: Message):
    await message.answer(get_translation('wrong_command'))