from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import db
import keyboards


async def show_category(message: types.Message):
    await message.answer("Выберите раздел: ", reply_markup=keyboards.get_categories_kb())


async def show_food_by_category(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    await callback_query.message.answer(f"{food[0]['name']}\n{food[0]['description']}\n{food[0]['price']}",
                                        reply_markup=keyboards.beautiful_change_of_food(0, len(food), categories[1]))


async def change_food_by_callback(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    if len(food) > int(categories[2]) >= 0:
        try:
            await callback_query.message.edit_text(f"{food[int(categories[2])]['name']}\n{food[int(categories[2])]['description']}\n{food[int(categories[2])]['price']}",
                                               reply_markup=keyboards.beautiful_change_of_food(int(categories[2]), len(food), categories[1]))
        except:
            await callback_query.answer()
    else:
        await callback_query.answer()


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(show_category, lambda m: m.text.startswith('🍽Меню'))
    dp.register_message_handler(show_category, commands=['menu'])
    dp.register_callback_query_handler(show_food_by_category, lambda c: c.data.startswith('category'))
    dp.register_callback_query_handler(change_food_by_callback, lambda c: c.data.startswith('food'))

