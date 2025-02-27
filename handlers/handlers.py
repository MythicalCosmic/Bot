from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from config.settings import get_translation
from database.database import *
from utils.utils import add_user, add_payement_movement
from keyboards.keyboards import *
from dotenv import load_dotenv
from config.bot_setup import bot
from datetime import datetime

load_dotenv(override=True)

CLICK_TOKEN = os.getenv("CLICK_TOKEN", "0")
PAYME_TOKEN = os.getenv("PAYME_TOKEN", "0")

router = Router()  

@router.message(Command("start"))
async def say_hi(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    channel_id = -1002312782001 
    video_message_id = 6  

    session = SessionLocal()
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

    if user:
        await bot.forward_message(chat_id=message.chat.id, from_chat_id=channel_id, message_id=video_message_id)
        await message.reply(get_translation('start_message'), reply_markup=main_keys, parse_mode='HTML')
    else:
        add_user(telegram_id, username, step="START")
        await bot.forward_message(chat_id=message.chat.id, from_chat_id=channel_id, message_id=video_message_id)
        await message.reply(get_translation('start_message'), reply_markup=main_keys, parse_mode='HTML')


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
async def handle_payement(message: Message):
        session = SessionLocal()
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        if not user: 
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return
        user.step = 'PAYMENT'
        session.commit()
        await message.reply(get_translation('payment_question'), reply_markup=payment_buttons, parse_mode='HTML')


@router.message(lambda message: message.text in [CLICK_BUTTON, PAYME])
async def handle_alright(message: Message):
    telegram_id = message.from_user.id
    payment_type = message.text.strip().capitalize()
    payment_tokens = {
    '💳 click': CLICK_TOKEN,
    '💳 payme': PAYME_TOKEN
    }   
    payment_type = payment_tokens.get(payment_type, payment_type)
    session = SessionLocal()
    try:
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        
        if not user:
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        user.step = 'PREMIUM_ALRIGHT_HANDLER'
        session.commit()
    
    finally:
        session.close()  
    prices = [LabeledPrice(label="Telegram Premium Subscription", amount=1000000)] 
    
    await message.reply_invoice(
        title="Telegram Premium",
        description="Unlock Telegram Premium features such as ad-free browsing, faster downloads, and exclusive stickers.",
        payload="premium_subscription",
        provider_token=payment_type,  
        currency="UZS",
        prices=prices,
        start_parameter="premium_upgrade",
        reply_markup=back_from_yes_button
    )


@router.pre_checkout_query(lambda _: True)  
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)



@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message):
    telegram_id = message.from_user.id
    total_price = message.successful_payment.total_amount / 100  
    generated_link = message.successful_payment.invoice_payload 
    date = datetime.now()
    
    add_payement_movement(telegram_id, date, generated_link, total_price)
    
    await message.reply(get_translation('thanks'), parse_mode='HTML', reply_markup=back_button)




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





@router.channel_post()
async def get_video_id(message: types.Message):
    print(f"Video message ID: {message.message_id}")
