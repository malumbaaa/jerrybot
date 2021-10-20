from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils.markdown import *

import db
import keyboards


async def show_category(message: types.Message):
    await message.answer("Выберите раздел: ", reply_markup=keyboards.get_categories_kb())


async def show_food_by_category(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    await callback_query.message.answer_photo(photo=food[0]['photo_id'],
                                              caption=bold(f"{food[0]['name']}\n\n") +
                                                      f"{food[0]['description']}\n\n" +
                                                      bold(f"{food[0]['price']} BYN\n"),
                                              parse_mode=ParseMode.MARKDOWN,
                                              reply_markup=keyboards.beautiful_change_of_food(0, len(food), categories[1]))


async def change_food_by_callback(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    current_food = int(categories[2])
    if len(food) > current_food >= 0:
        try:
            await callback_query.message.delete()
            await callback_query.message.answer_photo(photo=food[current_food]['photo_id'],
                                                      caption=bold(f"{food[current_food]['name']}\n\n") +
                                                              f"{food[current_food]['description']}\n\n" +
                                                              bold(f"{food[current_food]['price']} BYN\n"),
                                                      parse_mode=ParseMode.MARKDOWN,
                                                      reply_markup=keyboards
                                                      .beautiful_change_of_food(current_food,
                                                                                len(food),
                                                                                categories[1]))
        except:
            await callback_query.answer()
    else:
        await callback_query.answer()


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(show_category, lambda m: m.text.startswith('🍽Меню'))
    dp.register_message_handler(show_category, commands=['menu'])
    dp.register_callback_query_handler(show_food_by_category, lambda c: c.data.startswith('category'))
    dp.register_callback_query_handler(change_food_by_callback, lambda c: c.data.startswith('food'))

