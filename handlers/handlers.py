import traceback
from datetime import datetime

from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command

from config.settings import get_translation
from database.database import *
from utils.utils import add_user, add_payement_movement
from keyboards.keyboards import *
from dotenv import load_dotenv
from config.bot_setup import bot

load_dotenv(override=True)

CLICK_TOKEN = os.getenv("CLICK_TOKEN", "0")
PAYME_TOKEN = os.getenv("PAYME_TOKEN", "0")
CHANNEL_ID = os.getenv("CHANNEL_ID", "0")
VIDEO_MESSAGE_ID = os.getenv("VIDEO_MESSAGE_ID", "0")
ADMIN_ID = 5965983282

router = Router()


@router.message(Command("start"))
async def say_hi(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    session = SessionLocal()
    try:
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        if user is None:
            add_user(telegram_id, username, step="START")

        await bot.forward_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_ID)
        await message.reply(get_translation('start_message'), reply_markup=main_keys, parse_mode='HTML')
    except Exception as e:
        error_message = (
            f"❌ Ошибка в команде /start!\n\n"
            f"Chat ID: {message.chat.id}\n"
            f"User: @{username} ({telegram_id})\n"
            f"Message ID: {message.message_id}\n"
            f"Date: {message.date}\n\n"
            f"Error Type: {type(e).__name__}\n"
            f"Error Message: {str(e)}\n\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message, parse_mode='HTML')
        print(f"Error in start command: {e}")
    finally:
        session.close()


@router.message(lambda message: message.text == PREMIUM_KEY)
async def handle_premium(message: Message):
    session = SessionLocal()
    try:
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

        if not user:
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        user.step = 'PREMIUM_WARNING_HANDLER'
        session.commit()

        await message.reply(get_translation('premium_warning'), reply_markup=sure_buttons, parse_mode='HTML')
    except Exception as e:
        error_message = (
            f"❌ Premium handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.message(lambda message: message.text == SURE_OK)
async def handle_payement(message: Message):
    session = SessionLocal()
    try:
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

        if not user:
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        user.step = 'PAYMENT'
        session.commit()

        await message.reply(get_translation('payment_question'), reply_markup=payment_buttons, parse_mode='HTML')
    except Exception as e:
        error_message = (
            f"❌ Payment handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.message(lambda message: message.text in [CLICK_BUTTON, PAYME])
async def handle_alright(message: Message):
    telegram_id = message.from_user.id
    payment_type = message.text.strip().lower()
    payment_tokens = {
        '💳 click': CLICK_TOKEN,
        '💳 payme': PAYME_TOKEN
    }

    session = SessionLocal()
    try:
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
            provider_token=payment_tokens.get(payment_type, CLICK_TOKEN),
            currency="UZS",
            prices=prices,
            start_parameter="premium_upgrade",
            reply_markup=back_from_yes_button
        )
    except Exception as e:
        error_message = (
            f"❌ Payment setup error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Payment Type: {payment_type}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.pre_checkout_query(lambda _: True)
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as e:
        error_message = (
            f"❌ Pre-checkout error:\n"
            f"Query ID: {pre_checkout_query.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)


@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message):
    total_price = 0
    try:
        telegram_id = message.from_user.id
        total_price = message.successful_payment.total_amount / 100
        generated_link = message.successful_payment.invoice_payload
        date = datetime.now()

        add_payement_movement(telegram_id, date, generated_link, total_price)
        await message.reply(get_translation('thanks'), parse_mode='HTML', reply_markup=back_button)
    except Exception as e:
        error_message = (
            f"❌ Payment success handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Payment Amount: {total_price if 'total_price' in locals() else 'N/A'}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)


@router.message(lambda message: message.text == SMM_KEY)
async def handle_smm(message: Message):
    session = SessionLocal()
    try:
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        if not user:
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        await message.reply(get_translation('smm_intro'), parse_mode='HTML', reply_markup=smm_button)
    except Exception as e:
        error_message = (
            f"❌ SMM handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.message(lambda message: message.text == CONTACT)
async def handle_contact(message: Message):
    session = SessionLocal()
    try:
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

        if not user:
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        await message.reply(get_translation('contact_message'), parse_mode='HTML')
    except Exception as e:
        error_message = (
            f"❌ Contact handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.callback_query(lambda c: c.data == "go_back")
async def handle_back_inline(callback_query: CallbackQuery):
    session = SessionLocal()
    try:
        telegram_id = callback_query.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

        if not user:
            await callback_query.message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        user.step = 'START'
        session.commit()

        await callback_query.message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)
        await callback_query.answer()
    except Exception as e:
        error_message = (
            f"❌ Back inline handler error:\n"
            f"User ID: {callback_query.from_user.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.message(lambda message: message.text in [SURE_NOT, BACK])
async def handle_back(message: Message):
    session = SessionLocal()
    try:
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

        if not user:
            await message.reply(get_translation('wrong_command'), parse_mode='HTML')
            return

        user.step = 'START'
        session.commit()

        await message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)
    except Exception as e:
        error_message = (
            f"❌ Back handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.message()
async def fallback_handler(message: Message):
    session = SessionLocal()
    try:
        telegram_id = message.from_user.id
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()

        if user:
            user.step = 'START'
            session.commit()

        await message.reply(text=get_translation('wrong_command'), parse_mode='HTML')
        await message.answer(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)
    except Exception as e:
        error_message = (
            f"❌ Fallback handler error:\n"
            f"User ID: {message.from_user.id}\n"
            f"Message Text: {message.text}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
    finally:
        session.close()


@router.channel_post()
async def get_video_id(message: types.Message):
    try:
        print(f"Video message ID: {message.message_id}")
    except Exception as e:
        error_message = (
            f"❌ Channel post handler error:\n"
            f"Message ID: {message.message_id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)