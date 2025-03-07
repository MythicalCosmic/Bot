from database.database import TelegramUser, SessionLocal, PaymentMovement
from aiogram.types import ChatInviteLink
from datetime import datetime, timedelta
from aiogram.types import ChatInviteLink
import traceback

def add_user(telegram_id, username, step):
    
    session = SessionLocal()
    existing_user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
    
    if not existing_user:
        new_user = TelegramUser(
            telegram_id=telegram_id,
            username=username,
            step=step
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