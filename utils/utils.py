from database.database import TelegramUser, SessionLocal, PaymentMovement
from aiogram.types import ChatInviteLink, Message
from datetime import datetime
from config.settings import get_translation
import traceback
from keyboards.keyboards import *
from dotenv import load_dotenv
import os
import pytz

load_dotenv(override=True)


CLICK_TOKEN = os.getenv("CLICK_TOKEN", "0")
PAYME_TOKEN = os.getenv("PAYME_TOKEN", "0")
CHANNEL_ID = os.getenv("VIDEO_CHANNEL_ID", "0")
VIDEO_MESSAGE_ID = os.getenv("VIDEO_MESSAGE_ID", "0")
ADMIN_ID = os.getenv("ADMIN_ID", "0")
LINK_CHANNEL_ID = os.getenv('LINK_CHANNEL_ID')
TIMEZONE = os.getenv('TIMEZONE')

uzb_timezone = pytz.timezone(TIMEZONE)



VALID_STATES = {
    'START',
    'PREMIUM_WARNING_HANDLER',
    'PAYMENT',
    'PREMIUM_ALRIGHT_HANDLER'
}

def add_user(telegram_id, username, step, language):
    
    session = SessionLocal()
    existing_user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    
    if not existing_user:
        new_user = TelegramUser(
            telegram_id=telegram_id,
            username=username,
            step=step,
            language=language
        )
        session.add(new_user)
        session.commit()
        session.close()
        return True
    session.close()
    return False

def add_payement_movement(telegram_id, generated_link, total_price, payment_type):
    session = SessionLocal()
    try:
        payment_movement = PaymentMovement(
            telegram_id=telegram_id,
            generated_link=generated_link,
            total_price=total_price,
            payment_type=payment_type,
        )
        session.add(payment_movement)
        session.commit()
        session.refresh(payment_movement)  
        return payment_movement.id  
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()



async def generate_one_time_link(bot, channel_username: str):
    try:
        chat_invite_link: ChatInviteLink = await bot.create_chat_invite_link(
            chat_id=channel_username, 
            member_limit=1 
        )
        return chat_invite_link.invite_link  
    except Exception as e:
        return None

def format_error(context, message, error, user_id=None):
    base_info = f"❌ {context.capitalize()} error:\n"
    if message:
        base_info += (
            f"User ID: {message.from_user.id}\n"
            f"Username: @{message.from_user.username or 'N/A'}\n"
            f"Message Text: {message.text if hasattr(message, 'text') else 'N/A'}\n"
        )
    elif user_id:
        base_info += f"User ID: {user_id}\n"
    
    return (
        f"{base_info}"
        f"Error Type: {type(error).__name__}\n"
        f"Error Message: {str(error)}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )


def format_payment_success(message, total_price, payment_type, generated_link, payment_movement_id):
    current_time = datetime.now(uzb_timezone).strftime('%Y-%m-%d %H:%M:%S')
    formatted_price = f"{total_price:,.2f}"
    return (
        f"✅ Successful Payment Received!\n\n"
        f"User ID: {message.from_user.id}\n"
        f"Username: @{message.from_user.username or ''}\n"
        f"Full Name: {message.from_user.first_name} {message.from_user.last_name or ''}\n"
        f"Amount: {formatted_price} {message.successful_payment.currency}\n"
        f"Payment Type: {payment_type}\n"
        f"Payment Movement Id: {payment_movement_id}\n"
        f"Generated Link: {generated_link}\n"
        f"Date: {current_time}\n" 
    )



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
        'PREMIUM_WARNING_HANDLER': lambda: message.reply(get_translation('warning_message'), reply_markup=sure_buttons, parse_mode='HTML'),
        'PAYMENT': lambda: message.reply(get_translation('payment_type_message'), reply_markup=payment_buttons, parse_mode='HTML'),
        'PREMIUM_ALRIGHT_HANDLER': lambda: message.reply(get_translation('payment_type_message'), reply_markup=payment_buttons, parse_mode='HTML')
    }
    handler = state_handlers.get(user.step)
    if handler:
        await handler()