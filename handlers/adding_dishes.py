from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import *
from aiogram.types import ParseMode
from StateMachine import StateMachine

import db


class AddDish(StatesGroup):
    waiting_for_dish_name = State()
    waiting_for_dish_description = State()
    waiting_for_dish_price = State()
    waiting_for_dish_photo = State()


async def dish_name_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    await state.update_data(name=message.text)
    await AddDish.waiting_for_dish_description.set()
    await message.answer(bold(f"{message.text}\n") +
                         f"Напишите описание для блюда", parse_mode=ParseMode.MARKDOWN)


async def dish_description_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    name = (await state.get_data('name'))['name']
    await state.update_data(description=message.text)
    await AddDish.waiting_for_dish_price.set()
    await message.answer(bold(f"{name}\n\n") +
                         f"{message.text}\n\n"
                         f"Напишите цену для блюда", parse_mode=ParseMode.MARKDOWN)


async def dish_price_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    name = (await state.get_data('name'))['name']
    description = (await state.get_data('description'))['description']
    await state.update_data(price=message.text)
    await AddDish.waiting_for_dish_photo.set()
    await message.answer(bold(f"{name}\n\n") +
                         f"{description}\n\n" +
                         bold(f"{message.text} BYN\n") +
                         f"Отправьте фотографию блюда",
                         parse_mode=ParseMode.MARKDOWN)


async def dish_photo_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    name = (await state.get_data('name'))['name']
    description = (await state.get_data('description'))['description']
    price = (await state.get_data('price'))['price']
    photo_id = message.photo[-1].file_id
    db.add_dish(name, category, description, price, photo_id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton(text="✉Отправить рассылку✉"))
    kb.add(types.KeyboardButton(text="📊Посмотреть статистику📊"))
    kb.add(types.KeyboardButton(text="🍽Добавить блюдо🍽"))
    kb.add(types.KeyboardButton(text="❌Выйти из режима админа❌"))
    await state.set_state(StateMachine.all()[0])
    await message.answer_photo(photo=photo_id,
                               caption=bold(f"{name}\n\n") +
                                       f"{description}\n\n" +
                                       bold(f"{price} BYN\n"),
                               parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


def register_handlers_food(dp: Dispatcher):
    dp.register_message_handler(dish_name_handler, state=AddDish.waiting_for_dish_name)
    dp.register_message_handler(dish_description_handler, state=AddDish.waiting_for_dish_description)
    dp.register_message_handler(dish_price_handler, state=AddDish.waiting_for_dish_price)
    dp.register_message_handler(dish_photo_handler, content_types=['photo'], state=AddDish.waiting_for_dish_photo)
