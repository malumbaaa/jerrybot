from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup

import db
from StateMachine import NewStateMachine

from aiogram import Dispatcher, types


class StateMachineRegistration(StatesGroup):
    registration_phone_state = State()
    registration_name_state = State()


# функции регистрации
async def register_message(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(text="Зарегистрироваться", request_contact=True))
    name = message.text
    print("register name: " + message.text)
    if name == "" or not name.isalpha():
        await message.answer(f"Вам нужно корректно написать свою фамилию и имя!")
    else:
        await state.set_data(message.text)
        await message.answer(f"Нажмите кнопку ниже, чтобы поделиться с номером телефона", reply_markup=kb)
    await state.set_data(name)
    await StateMachineRegistration.registration_phone_state.set()  # set registration_phone_state


# функции регистрации
async def receive_contact_message(message: types.Message, state: FSMContext):
    rm_kb = types.ReplyKeyboardRemove()
    phone_number = message.contact.phone_number
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(text="🍽Меню🍽"))
    kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
    print("phone number " + message.contact.phone_number)
    if db.register_new_user(str(await state.get_data()), str(phone_number), str(message.from_user.id)):
        await message.answer('Вы успешно зарегистрировались', reply_markup=kb)
    else:
        await message.answer('Что-то пошло не так :(', reply_markup=rm_kb)
    await state.reset_state()


async def reg(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    if db.is_registered(telegram_id):
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton(text="🍽Меню🍽"))
        kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
        await message.answer(f"Вы уже зарегистрированы", reply_markup=kb)
        await state.reset_state()
    else:
        await StateMachineRegistration.registration_name_state.set()  # registration_name_state
        await message.answer("Напишите свое имя")


def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(reg, commands=['reg', 'start'])
    dp.register_message_handler(receive_contact_message, content_types=['contact'],
                                state=StateMachineRegistration.registration_phone_state)
    dp.register_message_handler(register_message, state=StateMachineRegistration.registration_name_state)
