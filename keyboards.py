import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import db


def table_choose(table_count: int, year, month, day):
    table_kb = InlineKeyboardMarkup(row_width=3)
    row = []
    for i in range(table_count):
        table_kb.add(InlineKeyboardButton(f"Стол №{i+1}", callback_data=f"table;{i+1};{year};{month};{day}"))
    return table_kb


def get_reserved_time(date: str, table: str) -> InlineKeyboardMarkup:
    time_kb = InlineKeyboardMarkup(row_width=5)
    buttons = []
    reserved_time = db.get_reserved_time(date, table)
    for hour in range(18, 24 + 4):
        if hour >= 24:
            hour -= 24
            hour = str(f"0{hour}")
        for minute in ['00', '30']:
            if f"{hour}:{minute}" not in reserved_time:
                buttons.append(InlineKeyboardButton(f"{hour}:{minute}", callback_data=f"time;{hour}:{minute};"
                                                                                      f"{table};{date}"))
            else:
                buttons.append(InlineKeyboardButton(f"     ", callback_data=f"reserved"))
    return time_kb.add(*buttons)


def get_categories_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []
    categories = db.get_categories()
    if len(categories) > 0:
        for category in categories:
            buttons.append(InlineKeyboardButton(f"{category['name']}", callback_data=f"category;{category['name']};1"))
    return keyboard.add(*buttons)


def yes_no_keyboard(number_in_queue):
    yes_no_kb = InlineKeyboardMarkup(row_width=2)
    yes_btn = InlineKeyboardButton("Да", callback_data="choose;yes")
    no_btn = InlineKeyboardButton("Нет", callback_data="choose;no")
    return yes_no_kb.add(yes_btn, no_btn)


def time_choose():
    time_kb = InlineKeyboardMarkup(row_width=8)
    for hour in range(17, 6):
        for minute in ['00', '30']:
            time_kb.add(InlineKeyboardButton(f"{hour}.{minute}", callback_data=f"time;{hour};{minute}"))
    return time_kb


def beautiful_change_of_food(current_food, count_food, category):
    food_changing_kb = InlineKeyboardMarkup(row_width=3)
    left_btn = InlineKeyboardButton("⬅️", callback_data=f"food;{category};{int(current_food)-1}")
    right_btn = InlineKeyboardButton("➡️", callback_data=f"food;{category};{int(current_food)+1}")
    count_btn = InlineKeyboardButton(f"{current_food+1}/{count_food}", callback_data=f'food;{category};0')
    return food_changing_kb.add(left_btn, count_btn, right_btn)
