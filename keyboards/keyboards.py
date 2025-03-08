from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


PREMIUM_KEY = "🌟 Yopiq kanalga qo'shilish"
SMM_KEY = "📣 Marketing xizmati"
CONTACT = "📞💻 Dasturchi bilan bog‘lanish"  
SURE_OK = "🚀 Kanalga qo'shilmoqchiman"
SURE_NOT = "❌ Yo‘q, orqaga qaytish"  
BUY_NOW = "💰 Sotib olish"  
BACK = "🔙 Orqaga"  
CLICK_BUTTON = "💳 Click"  
PAYME = "💳 Payme"
CONSULTATION_KEY = "💬 Konsultatsiyaga yozilish"

main_keys = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=PREMIUM_KEY), KeyboardButton(text=CONSULTATION_KEY)],
        [KeyboardButton(text=CONTACT), KeyboardButton(text=SMM_KEY)]
    ],
    resize_keyboard=True
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
)


back_from_yes_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=BUY_NOW, pay=True)]
    ]
)

back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BACK)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

smm_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💬 Mutaxasisga yozish", url="https://telegram.org/JasonDevOps")],
    ]
)