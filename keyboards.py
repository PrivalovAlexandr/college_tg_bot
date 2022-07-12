from aiogram import types
from config import *

kb_menu = (
    types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    .add (*menu_key[:2])
    .add (*menu_key[2:])
)

kb_role = (
    types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    .add(*role)
)

kb_corpus = (
    types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    .add(*corpus)
)

kb_course = (
    types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    .add(*course)
)

kb_proof = (
    types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    .add(*('Да', 'Нет'))
)