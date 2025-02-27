import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(255), nullable=True)
    step = Column(String(250))


class PaymentMovement(Base):
    __tablename__ = "payment_movements"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, ForeignKey('telegram_users.id'))
    date = Column(Date)
    generated_link = Column(String)
    total_price = Column(DECIMAL(20, 2))
