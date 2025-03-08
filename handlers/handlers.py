from aiogram import Router, types, Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from config.settings import get_translation
from database.database import *
from utils.utils import *
from keyboards.keyboards import *
from config.bot_setup import bot

router = Router()


@router.message(Command("start"))
async def say_hi(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    session = SessionLocal()
    try:
        user = session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        if not user:
            add_user(telegram_id, username, step="START", language="uz")
        else:
            user.step = "START"
            session.commit()
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
            if not user:  
                await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
                return
            await send_state_message(message, user)
            return

        user.step = 'PREMIUM_WARNING_HANDLER'
        session.commit()
        await message.reply(get_translation('warning_message'), reply_markup=sure_buttons, parse_mode='HTML')
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
            if not user: 
                await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
                return
            await send_state_message(message, user)
            return

        user.step = 'PAYMENT'
        session.commit()
        await message.reply(get_translation('payment_type_message'), reply_markup=payment_buttons, parse_mode='HTML')
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
            if not user:  
                await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
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
            if not user: 
                await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
                return
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

        await message.reply(get_translation('success_message').replace(':link',generated_link), parse_mode='HTML', reply_markup=main_keys)
        await message.answer(generated_link)
        
        await bot.send_message(ADMIN_ID, format_payment_success(message, total_price, payment_type, generated_link, payment_movement_id))
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
            if not user:  
                await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
                return
            await send_state_message(message, user)
            return

        await message.reply(get_translation('smm_message'), parse_mode='HTML', reply_markup=smm_button)
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
            if not user:  
                await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
                return
            await send_state_message(message, user)
            return

        await message.reply(get_translation('it_service_message'), parse_mode='HTML')
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("contact handler", message, e))
    finally:
        session.close()

@router.message(lambda message: message.text in [SURE_NOT, BACK])
async def handle_back(message: Message):
    session = SessionLocal()
    try:
        user = check_user_and_state(session, message.from_user.id)
        if not user:  
            await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
            return

        if message.text == BACK:
            user.step = 'PREMIUM_WARNING_HANDLER'
            await message.reply(get_translation('warning_message'), parse_mode='HTML', reply_markup=sure_buttons)
        else:  
            user.step = 'START'
            await message.reply(get_translation('start_message'), parse_mode='HTML', reply_markup=main_keys)

        session.commit()
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
            await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
            return

        if user.step is None:
            await message.reply(get_translation('wrong_command_message'), parse_mode='HTML')
            return

        await send_state_message(message, user)
    except Exception as e:
        await bot.send_message(ADMIN_ID, format_error("fallback", message, e))
    finally:
        session.close()

