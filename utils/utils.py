from database.database import TelegramUser, SessionLocal

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