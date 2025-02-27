from database.database import TelegramUser, SessionLocal, PaymentMovement

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

def add_payement_movement(telegram_id, date, generated_link, total_price):
    session = SessionLocal()
    new_payment_movement = PaymentMovement(
        telegram_id=telegram_id,
        date=date,
        generated_link=generated_link,
        total_price=total_price
    )
    session.add(new_payment_movement)
    session.commit()
    return True