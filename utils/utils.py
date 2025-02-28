from database.database import TelegramUser, SessionLocal, PaymentMovement
from aiogram.types import ChatInviteLink
from datetime import datetime, timedelta
from aiogram.types import ChatInviteLink

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

def add_payement_movement(telegram_id, date, generated_link, total_price, payment_type):
    session = SessionLocal()
    new_payment_movement = PaymentMovement(
        telegram_id=telegram_id,
        date=date,
        generated_link=generated_link,
        total_price=total_price,
        payment_type=payment_type
    )
    session.add(new_payment_movement)
    session.commit()
    return True



async def generate_one_time_link(bot, channel_username: str):
    try:
        chat_invite_link: ChatInviteLink = await bot.create_chat_invite_link(
            chat_id=channel_username, 
            member_limit=1 
        )
        return chat_invite_link.invite_link  
    except Exception as e:
        return None
