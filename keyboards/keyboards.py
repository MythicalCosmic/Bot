from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
PREMIUM_KEY = "🌟 Upgrade to Premium"  
SMM_KEY = "📣 Social Media Services"  
CONTACT = "📞💻 Contact the Developer"
SURE_OK = "✔️ Yes, I agree"  
SURE_NOT = "❌ No, go back"  
BUY_NOW = "💰 Purchase Now"  
BACK = "🔙 Back"  
CLICK_BUTTON = "💳 Click"
PAYME =  "💳 Payme"


main_keys = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=PREMIUM_KEY), KeyboardButton(text=SMM_KEY)],
        [KeyboardButton(text=CONTACT)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

sure_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SURE_OK)],
        [KeyboardButton(text=SURE_NOT)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

payment_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=CLICK_BUTTON), KeyboardButton(text=PAYME)],
        [KeyboardButton(text=BACK)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


back_from_yes_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=BUY_NOW, pay=True)],
        [InlineKeyboardButton(text=SURE_NOT, callback_data="go_back")]
    ]
)

back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BACK)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
