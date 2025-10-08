from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

phone_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Telefon raqam yuborish", request_contact=True)
        ]
    ],resize_keyboard=True
)

location_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Location yuborish", request_location=True)
        ]
    ],resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='All users'),
            KeyboardButton(text='Add hospital'),
            KeyboardButton(text='All hospitals')
        ],
        [
            KeyboardButton(text='Add doctor'),
            KeyboardButton(text='All doctors'),
            KeyboardButton(text='All bookings')
        ]
    ]
)