from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
PREMIUM_KEY = "🌟 Premiumga olish"  
SMM_KEY = "📣 SMM xizmati"  
CONTACT = "📞💻 Dasturchi bilan bog‘lanish"  
SURE_OK = "✔️ Ha, roziman"  
SURE_NOT = "❌ Yo‘q, orqaga qaytish"  
BUY_NOW = "💰 Sotib olish"  
BACK = "🔙 Orqaga"  
CLICK_BUTTON = "💳 Click"  
PAYME = "💳 Payme"


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
