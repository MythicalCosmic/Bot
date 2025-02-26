from aiogram import Router, types
from aiogram.types import Message, FSInputFile, CallbackQuery, LabeledPrice
from aiogram.filters import Command
from config.settings import get_translation
from database.database import *
from utils.utils import add_user
from keyboards.keyboards import *

CLICK_TOKEN = '371317599:TEST:1740546139453'
PAYME_TOKEN = '371317599:TEST:1740549200011'

router = Router()  

@router.message(Command("start"))  
async def say_hi(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    paht_video = "./media/videos/video.mp4"

    session = SessionLocal()

    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    if user:
        await message.reply_video(video=FSInputFile(paht_video), caption=get_translation('start_message'), reply_markup=main_keys, parse_mode='HTML')
    else:
        add_user(telegram_id, username, step="START")
        await message.reply_video(video=FSInputFile(paht_video), caption=get_translation('start_message'), reply_markup=main_keys, parse_mode='HTML')


@router.message(lambda message: message.text == PREMIUM_KEY)
async def handle_premium(message: Message):
    session = SessionLocal()
    telegram_id = message.from_user.id
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    if not user:
        await message.reply(get_translation('wrong_command'), parse_mode='HTML')
        return
    user.step = 'PREMIUM_WARNING_HANDLER'
    session.commit()
    await message.reply(get_translation('premium_warning'), reply_markup=sure_buttons, parse_mode='HTML')



@router.message(lambda message: message.text == SURE_OK)
async def handle_alright(message: Message):
    telegram_id = message.from_user.id
    session = SessionLocal()
    
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    
    if not user:
        await message.reply(get_translation('wrong_command'), parse_mode='HTML')
        return

    user.step = 'PREMIUM_ALRIGHT_HANDLER'
    session.commit()
    prices = [LabeledPrice(label="Telegram Premium Subscription", amount=1000000)] 
    await message.reply_invoice(
        title="Telegram Premium",
        description="Unlock Telegram Premium features such as ad-free browsing, faster downloads, and exclusive stickers.",
        payload="premium_subscription",
        provider_token=CLICK_TOKEN,  
        currency="UZS",
        prices=prices,
        start_parameter="premium_upgrade",
        reply_markup=back_from_yes_button
    )



@router.message(lambda message: message.text == SMM_KEY)
async def handle_smm(message: Message):
    telegram_id = message.from_user.id
    session = SessionLocal()
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    if not user:
        await message.reply(get_translation('wrong_command'), parse_mode='HTML')
        return
    user.step = 'SMM_SECTION'
    session.commit()
    await message.reply(get_translation('smm_intro'), parse_mode='HTML', reply_markup=back_button)


@router.message(lambda message: message.text == CONTACT)
async def handle_contact(message: Message):
    telegram_id = message.from_user.id
    session = SessionLocal()
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    if not user:
        await message.reply(get_translation('wrong_command'), parse_mode='HTML')
        return
    user.step = "CONTACT"
    session.commit()
    await message.reply(get_translation('contact_message'), parse_mode='HTML', reply_markup=back_button)


@router.callback_query(lambda c: c.data == "go_back")
async def handle_back_inline(callback_query: CallbackQuery):
    
    telegram_id = callback_query.from_user.id
    session = SessionLocal()
    
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first() 
    
    if not user:
        await callback_query.message.reply(get_translation('wrong_command'), parse_mode='HTML')
    else:
        user.step = 'START'
        session.commit()
        await callback_query.message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)
    
    await callback_query.answer() 


@router.message(lambda message: message.text in [SURE_NOT, BACK])  
async def handle_back(message: Message):
    telegram_id = message.from_user.id
    session = SessionLocal()
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    if not user:
        await message.reply(get_translation('wrong_command'), parse_mode='HTML')
        return
    user.step = 'START'
    session.commit()
    await message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)



@router.message()
async def fallback_handler(message: Message):
    session = SessionLocal()
    telegram_id = message.from_user.id
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    user.step = 'START'
    session.commit()
    await message.reply(text=get_translation('wrong_command'), parse_mode='HTML')
    await message.answer(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)



