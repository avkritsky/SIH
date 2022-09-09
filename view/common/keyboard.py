from typing import Union

from aiogram import types


def get_start_menu():
    menu_titles = (
        'Statistics',
        'Add',
        'Del',
        'Clear',
        'Settings',
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*menu_titles)

    return keyboard


def create_keyboard(menu_titles: Union[tuple, list]):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*menu_titles)

    return keyboard
