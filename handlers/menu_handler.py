from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils.markdown import *

import db
import keyboards


class Menu(StatesGroup):
    already_take_smth = State()
    open_cart = State()


async def show_category(message: types.Message):
    await message.answer("Выберите раздел: ", reply_markup=keyboards.get_categories_kb())


async def show_food_by_category(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    try:
        await callback_query.message.answer_photo(photo=food[0]['photo_id'],
                                                  caption=bold(f"{food[0]['name']}\n\n") +
                                                          f"{food[0]['description']}\n\n" +
                                                          bold(f"{food[0]['price']} BYN\n"),
                                                  parse_mode=ParseMode.MARKDOWN,
                                                  reply_markup=keyboards.beautiful_change_of_food(0, len(food),
                                                                                                  categories[1],
                                                                                                  food[0]['name'], 'add'))
    except IndexError:
        await callback_query.message.answer(text="В этой категории нет еды")
    await Menu.already_take_smth.set()


async def change_food_by_callback(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    current_food = int(categories[2])
    if len(food) > current_food >= 0:
        try:
            next_photo = types.input_media.InputMediaPhoto(str='photo', media=food[current_food]['photo_id'],
                                                           caption=bold(f"{food[current_food]['name']}\n\n") +
                                                              f"{food[current_food]['description']}\n\n" +
                                                              bold(f"{food[current_food]['price']} BYN\n"),
                                                           parse_mode = ParseMode.MARKDOWN)
            await callback_query.message.edit_media(media=next_photo,
                                                    reply_markup=keyboards
                                                   .beautiful_change_of_food(current_food,
                                                                             len(food),
                                                                             categories[1],
                                                                             food[current_food]['name'], 'add'))
        except:
            await callback_query.answer()
    else:
        await callback_query.answer()


async def add_food_to_cart(callback_query: types.CallbackQuery,  state: FSMContext):
    categories = callback_query.data.split(';')
    previous_order = await state.get_data()
    try:
        await state.update_data(food=previous_order['food']+";"+categories[1])
    except KeyError:
        await state.update_data(food=categories[1])
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(text="🍽Меню🍽"))
    kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
    kb.add(types.KeyboardButton(text="🛒Посмотреть корзину🛒"))
    await callback_query.message.answer(text='Заказ принят', reply_markup=kb)


async def check_cart(message: types.Message, state: FSMContext):
    order = await state.get_data()
    foods = order['food'].split(';')
    data = []
    for food in foods:
        data.append(db.get_food_by_name(food))
    try:
        await message.answer_photo(photo=data[0]['photo_id'],
                                                      caption=bold(f"{data[0]['name']}\n\n") +
                                                              f"{data[0]['description']}\n\n" +
                                                              bold(f"{data[0]['price']} BYN\n"),
                                                      parse_mode=ParseMode.MARKDOWN,
                                                      reply_markup=keyboards.beautiful_change_of_food(0, len(data),
                                                                                                      '',
                                                                                                      data[0]['name'],
                                                                                                      'remove'))
        await Menu.open_cart.set()
        await state.set_data(order)
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton(text="💰Купить💰"))
        kb.add(types.KeyboardButton(text="🔙Вернуться в главное меню🔙"))
        await message.answer(text='аа, хз, как это меняь', reply_markup=kb)
    except TypeError:
        await message.answer(text='Корзина пока пуста')


async def change_food_in_cart(callback_query: types.CallbackQuery, state: FSMContext):
    categories = callback_query.data.split(';')
    order = await state.get_data()
    foods = order['food'].split(';')
    data = []
    current_food = int(categories[2])
    for food in foods:
        data.append(db.get_food_by_name(food))
    if len(data) > current_food >= 0:
        try:
            next_photo = types.input_media.InputMediaPhoto(str='photo', media=data[current_food]['photo_id'],
                                                           caption=bold(f"{data[current_food]['name']}\n\n") +
                                                              f"{data[current_food]['description']}\n\n" +
                                                              bold(f"{data[current_food]['price']} BYN\n"),
                                                           parse_mode = ParseMode.MARKDOWN)
            await callback_query.message.edit_media(media=next_photo,
                                                    reply_markup=keyboards
                                                   .beautiful_change_of_food(current_food,
                                                                             len(data),
                                                                             categories[1],
                                                                             data[current_food]['name'], 'remove'))
        except:
            await callback_query.answer()
    else:
        await callback_query.answer()


async def back_to_main_menu(message: types.Message, state: FSMContext):
    order = await state.get_data()
    await Menu.already_take_smth.set()
    await state.set_data(order)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(text="🍽Меню🍽"))
    kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
    kb.add(types.KeyboardButton(text="🛒Посмотреть корзину🛒"))
    await message.answer(text='Главное меню', reply_markup=kb)


async def remove_food_from_cart(callback_query: types.CallbackQuery,  state: FSMContext):
    categories = callback_query.data.split(';')
    order = await state.get_data()
    order['food'] = order['food'].replace(f";{categories[1]}", "")
    order['food'] = order['food'].replace(f"{categories[1]};", "")
    order['food'] = order['food'].replace(f"{categories[1]}", "")
    await state.set_data(order)
    foods = order['food'].split(';')
    data = []
    for food in foods:
        data.append(db.get_food_by_name(food))
    try:
        await callback_query.message.answer_photo(photo=data[0]['photo_id'],
                               caption=bold(f"{data[0]['name']}\n\n") +
                                       f"{data[0]['description']}\n\n" +
                                       bold(f"{data[0]['price']} BYN\n"),
                               parse_mode=ParseMode.MARKDOWN,
                               reply_markup=keyboards.beautiful_change_of_food(0, len(data),
                                                                               '',
                                                                               data[0]['name'],
                                                                               'remove'))
    except TypeError:
        await callback_query.message.answer(text='В корзине не осталось товаров')


async def buy_products(message: types.Message,  state: FSMContext):
    order = await state.get_data()
    if order:
        foods = order['food'].split(';')
        data = []
        for food in foods:
            data.append(db.get_food_by_name(food))
        db.add_order(message.chat.id, order['food'])
        await state.reset_state()
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton(text="🍽Меню🍽"))
        kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
        await message.answer(f"Ожидайте заказ", reply_markup=kb)
    else:
        await message.answer(f"Сначала закажите что-нибудь")


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(show_category, lambda m: m.text.startswith('🍽Меню'))
    dp.register_message_handler(show_category, commands=['menu'])
    dp.register_message_handler(show_category, lambda m: m.text.startswith('🍽Меню'), state=Menu.already_take_smth)
    dp.register_callback_query_handler(show_food_by_category, lambda c: c.data.startswith('category'))
    dp.register_callback_query_handler(show_food_by_category, lambda c: c.data.startswith('category'), state=Menu.already_take_smth )
    dp.register_callback_query_handler(change_food_by_callback, lambda c: c.data.startswith('food'), state=Menu.already_take_smth)
    dp.register_callback_query_handler(add_food_to_cart, lambda c: c.data.startswith('cart'), state=Menu.already_take_smth)
    dp.register_message_handler(check_cart, lambda m: m.text.startswith('🛒Посмотреть корзину'), state=Menu.already_take_smth)
    dp.register_callback_query_handler(change_food_in_cart, lambda c: c.data.startswith('food'),
                                       state=Menu.open_cart)
    dp.register_message_handler(back_to_main_menu, lambda m: m.text.startswith('🔙Вернуться в главное меню'),
                                state=Menu.open_cart)
    dp.register_callback_query_handler(remove_food_from_cart, lambda c: c.data.startswith('cart'),
                                       state=Menu.open_cart)
    dp.register_message_handler(buy_products, lambda m: m.text.startswith('💰Купить'),
                                state=Menu.open_cart)
