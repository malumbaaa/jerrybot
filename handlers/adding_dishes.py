from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

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
    await message.answer(f"{category}->{message.text}\n"
                         f"Напишите описание для блюда")


async def dish_description_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    name = (await state.get_data('name'))['name']
    await state.update_data(description=message.text)
    await AddDish.waiting_for_dish_price.set()
    await message.answer(f"{category}->{name}->{message.text}\n"
                         f"Напишите цену для блюда")


async def dish_price_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    name = (await state.get_data('name'))['name']
    description = (await state.get_data('description'))['description']
    await state.update_data(price=message.text)
    await AddDish.waiting_for_dish_photo.set()
    await message.answer(f"{category}->{name}->{description}->{message.text}\n"
                         f"Отправьте фотографию блюда(пока фича в разработке, просто отправь любое сообщение)")


async def dish_photo_handler(message: types.message, state: FSMContext):
    category = (await state.get_data('category'))['category']
    name = (await state.get_data('name'))['name']
    description = (await state.get_data('description'))['description']
    price = (await state.get_data('price'))['price']
    db.add_dish(name, category, description, price)
    await state.reset_state()
    await message.answer(f"{category}->{name}->{description}->{price}\n"
                         f"Блюдо добавлено!")


async def food_start(message: types.Message):
    await AddDish.waiting_for_dish_name.set()
    await message.answer(f"Test Message, state changed")


def register_handlers_food(dp: Dispatcher):
    dp.register_message_handler(food_start, commands="food", state="*")
    dp.register_message_handler(dish_name_handler, state=AddDish.waiting_for_dish_name)
    dp.register_message_handler(dish_description_handler, state=AddDish.waiting_for_dish_description)
    dp.register_message_handler(dish_price_handler, state=AddDish.waiting_for_dish_price)
    dp.register_message_handler(dish_photo_handler, state=AddDish.waiting_for_dish_photo)
