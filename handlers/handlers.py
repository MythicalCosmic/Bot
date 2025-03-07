
from datetime import datetime
from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from config.settings import get_translation
from database.database import *
from utils.utils import *
from keyboards.keyboards import *
from dotenv import load_dotenv
from config.bot_setup import bot

load_dotenv(override=True)

CLICK_TOKEN = os.getenv("CLICK_TOKEN", "0")
PAYME_TOKEN = os.getenv("PAYME_TOKEN", "0")
CHANNEL_ID = os.getenv("VIDEO_CHANNEL_ID", "0")
VIDEO_MESSAGE_ID = os.getenv("VIDEO_MESSAGE_ID", "0")
ADMIN_ID = os.getenv("ADMIN_ID", "0")
LINK_CHANNEL_ID = os.getenv('LINK_CHANNEL_ID')

router = Router()


VALID_STATES = {
    'START',
    'PREMIUM_WARNING_HANDLER',
    'PAYMENT',
    'PREMIUM_ALRIGHT_HANDLER'
}

def check_user_and_state(session, telegram_id, expected_state=None):
    user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    if not user:
        return None
    if expected_state and user.step not in VALID_STATES:
        user.step = 'START'
        session.commit()
    if expected_state and user.step != expected_state:
        return None
    return user

async def send_state_message(message: Message, user):
    state_handlers = {
        'START': lambda: message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys),
        'PREMIUM_WARNING_HANDLER': lambda: message.reply(get_translation('premium_warning'), reply_markup=sure_buttons, parse_mode='HTML'),
        'PAYMENT': lambda: message.reply(get_translation('payment_question'), reply_markup=payment_buttons, parse_mode='HTML'),
        'PREMIUM_ALRIGHT_HANDLER': lambda: message.reply(get_translation('payment_question'), reply_markup=payment_buttons, parse_mode='HTML')
    }
    handler = state_handlers.get(user.step)
    if handler:
        await handler()

@router.message(Command("start"))
async def say_hi(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    session = SessionLocal()
    try:
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        if not user:
            add_user(telegram_id, username, step="START")
        
        await bot.forward_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_ID)
        await message.reply(get_translation('start_message'), reply_markup=main_keys, parse_mode='HTML')
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("start", message, e))
    finally:
        session.close()

@router.message(lambda message: message.text == PREMIUM_KEY)
async def handle_premium(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id, 'START')
        if not user:
            user = check_user_and_state(session, message.from_user.id)
            if user:
                await send_state_message(message, user)
            return

        user.step = 'PREMIUM_WARNING_HANDLER'
        session.commit()
        await message.reply(get_translation('premium_warning'), reply_markup=sure_buttons, parse_mode='HTML')
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("premium handler", message, e))
    finally:
        session.close()

@router.message(lambda message: message.text == SURE_OK)
async def handle_payment(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id, 'PREMIUM_WARNING_HANDLER')
        if not user:
            user = check_user_and_state(session, message.from_user.id)
            if user:
                await send_state_message(message, user)
            return

        user.step = 'PAYMENT'
        session.commit()
        await message.reply(get_translation('payment_question'), reply_markup=payment_buttons, parse_mode='HTML')
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("payment handler", message, e))
    finally:
        session.close()

@router.message(lambda message: message.text in [CLICK_BUTTON, PAYME])
async def handle_alright(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id, 'PAYMENT')
        if not user:
            user = check_user_and_state(session, message.from_user.id)
            if user:
                await send_state_message(message, user)
            return

        payment_type = message.text.strip().lower()
        payment_tokens = {
            '💳 click': CLICK_TOKEN,
            '💳 payme': PAYME_TOKEN
        }
        
        user.step = 'PREMIUM_ALRIGHT_HANDLER'
        session.commit()

        prices = [LabeledPrice(label="Telegram Premium Subscription", amount=1000000)]
        await message.reply_invoice(
            title=f"Telegram Premium {payment_type.removeprefix('💳 ').upper()}",
            description="Telegram premium bilan koplab narsalari oching!.",
            payload=f"{payment_type.removeprefix('💳 ').upper()}",
            provider_token=payment_tokens.get(payment_type, CLICK_TOKEN),
            currency="UZS",
            prices=prices,
            start_parameter="premium_upgrade",
            reply_markup=back_from_yes_button
        )
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("payment setup", message, e))
    finally:
        session.close()

@router.pre_checkout_query(lambda _: True)
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("pre-checkout", None, e, pre_checkout_query.id))

@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id, 'PREMIUM_ALRIGHT_HANDLER')
        if not user:
            user = check_user_and_state(session, message.from_user.id)
            if user:
                await send_state_message(message, user)
            return

        total_price = message.successful_payment.total_amount / 100
        payment_type = message.successful_payment.invoice_payload
        generated_link = await generate_one_time_link(bot, LINK_CHANNEL_ID)
        
        payment_movement_id = add_payement_movement(
            message.from_user.id,
            generated_link,
            total_price,
            payment_type
        )

        user.step = 'START'
        session.commit()

        await message.reply(get_translation('thanks'), parse_mode='HTML', reply_markup=back_button)
        await message.answer(generated_link)
        
        await bot.send_message(ADMIN_ID, _format_payment_success(message, total_price, payment_type, generated_link, payment_movement_id))
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("payment success", message, e))
    finally:
        session.close()

@router.message(lambda message: message.text == SMM_KEY)
async def handle_smm(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id, 'START')
        if not user:
            user = check_user_and_state(session, message.from_user.id)
            if user:
                await send_state_message(message, user)
            return

        await message.reply(get_translation('smm_intro'), parse_mode='HTML', reply_markup=smm_button)
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("SMM handler", message, e))
    finally:
        session.close()

@router.message(lambda message: message.text == CONTACT)
async def handle_contact(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id, 'START')
        if not user:
            user = check_user_and_state(session, message.from_user.id)
            if user:
                await send_state_message(message, user)
            return

        await message.reply(get_translation('contact_message'), parse_mode='HTML')
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("contact handler", message, e))
    finally:
        session.close()

@router.callback_query(lambda c: c.data == "go_back")
async def handle_back_inline(callback_query: CallbackQuery):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, callback_query.from_user.id)
        if not user:
            return

        user.step = 'START'
        session.commit()
        
        await callback_query.message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)
        await callback_query.answer()
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("back inline", None, e, callback_query.from_user.id))
    finally:
        session.close()

@router.message(lambda message: message.text in [SURE_NOT, BACK])
async def handle_back(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id)
        if not user:
            return

        user.step = 'START'
        session.commit()
        await message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("back handler", message, e))
    finally:
        session.close()

@router.message()
async def fallback_handler(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id)
        if not user:
            return

        await send_state_message(message, user)
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("fallback", message, e))
    finally:
        session.close()


def _format_payment_success(message, total_price, payment_type, generated_link, payment_movement_id):
    return (
        f"✅ Successful Payment Received!\n\n"
        f"User ID: {message.from_user.id}\n"
        f"Username: @{message.from_user.username or 'N/A'}\n"
        f"First Name: {message.from_user.first_name or 'No first name'}\n"
        f"Last Name: {message.from_user.last_name or 'No last name'}\n"
        f"Amount: {total_price} {message.successful_payment.currency}\n"
        f"Payment Type: {payment_type}\n"
        f"Payment Movement Id: {payment_movement_id}\n"
        f"Generated Link: {generated_link}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Provider Payment Charge ID: {message.successful_payment.provider_payment_charge_id}\n"
        f"Telegram Payment Charge ID: {message.successful_payment.telegram_payment_charge_id}\n"
        f"Chat ID: {message.chat.id}\n"
        f"Message ID: {message.message_id}"
    )

# @router.channel_post()
# async def get_video_id(message: types.Message):
#     try:
#         print(f"Video message ID: {message.message_id}")
#     except Exception as e:
#         error_message = (
#             f"❌ Channel post handler error:\n"
#             f"Message ID: {message.message_id}\n"
#             f"Error: {str(e)}\n"
#             f"Traceback:\n{traceback.format_exc()}"
#         )
#         await bot.send_message(ADMIN_ID, error_message)