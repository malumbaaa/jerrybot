# Ссылка на статью про машину состояний, почитай обязательно перед тем, как делать
# https://surik00.gitbooks.io/aiogram-lessons/content/chapter3.html
import json
import logging

import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


import db
from StateMachine import StateMachine
import config
import TGCalendar.telegramcalendar as tgcalendar
from aiogram import Bot, Dispatcher, executor, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['anekdot'])
async def random_anekdot(message: types.Message):
    try:
        url = "http://rzhunemogu.ru/RandJSON.aspx?CType=11"
        r = requests.get(url=url)
        raw = r.text.replace("\n", " ").replace("\r", " ")
        print(raw)
        anekdot = json.loads(raw)
        await message.answer(anekdot["content"])
    except json.decoder.JSONDecodeError:
        await message.answer("Что-то пошло не так :(\nПопробуйте еще раз")


@dp.message_handler(state=StateMachine.PEOPLE_NUMBER)  # функция вывода заказа
async def people_number_message(message: types.Message):
    if message.text.isdigit():
        state = dp.current_state(user=message.chat.id)
        separated_data = str(await state.get_data()).split(";")
        db.reserve_table(separated_data[1], f"{separated_data[2]}-{separated_data[3]}-{separated_data[4]}",
                         message.text, message.from_user.id)
        await state.reset_state()
        await message.answer(f"Вы заказали "
                             f"стол №{separated_data[1]}\n"
                             f"{separated_data[4]}-{separated_data[3]}-{separated_data[2]}\n"
                             f"на {message.text} человек")
    else:
        await message.answer('Вы ввели некорректное количество людей, повторите ввод')


# @dp.callback_query_handler(lambda c: c.data.startswith('table'))  # функция для выбора времени
# async def people_time_message(callback_query: types.CallbackQuery):
#     state = dp.current_state(user=callback_query.message.chat.id)
#     separated_data = callback_query.data.split(";")
#     time_kb = InlineKeyboardMarkup(row_width=7)
#     buttons = []
#     for hour in range(17, 6):
#         for minute in ['00', '30']:
#             buttons.append(types.InlineKeyboardButton(f"{hour}.{minute}", callback_data=f"time;{hour}.{minute}"))
#     time_kb.add(*buttons)
#     print(time_kb.values)
#     await bot.answer_callback_query(callback_query.id)
#     await state.set_data(callback_query.data)
#     await state.set_state(StateMachine.all()[3])  # set people time set
#     await bot.edit_message_text(text=f"Выберите время", reply_markup=time_kb, chat_id=callback_query.message.chat.id,
#                                 message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data.startswith('DAY'), state=StateMachine.ADMIN) # функция вывода заказанных столов и админа
async def table_choose_callback(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    separated_data = callback_query.data.split(";")
    await bot.answer_callback_query(callback_query.id)
    tables = db.get_reservations(f"{separated_data[1]}-{separated_data[2]}-{separated_data[3]}")
    if len(tables) > 0:
        for res in tables:
            await bot.send_message(text=f"{res['date']}\n"
                                        f"{res['user_name']}\n"
                                        f"{res['user_phone']}\n"
                                        f"Стол №{res['table_number']} на {res['people_count']} человек",
                                   chat_id=callback_query.message.chat.id)
    else:
        await bot.send_message(text="В этот день записей нет :(", chat_id=callback_query.message.chat.id)


@dp.callback_query_handler(lambda c: c.data.startswith('table')) # функция ввода количества людей
async def table_choose_callback(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    separated_data = callback_query.data.split(";")
    await bot.answer_callback_query(callback_query.id)
    await state.set_data(callback_query.data)
    await state.set_state(StateMachine.all()[2])  # set people_number state
    await bot.edit_message_text(text=f"Вы выбрали "
                                     f"стол №{separated_data[1]}\n"
                                     f"{separated_data[4]}-{separated_data[3]}-{separated_data[2]}\n"
                                     f"Напишите количество человек:",
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id)


@dp.message_handler(commands=['admin']) # функция перехода в режим админа
async def set_admin_state(message: types.Message):
    if str(message.from_user.id) in config.ADMIN_IDS:
        state = dp.current_state(user=message.chat.id)
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(text="Выйти из режима админа"))
        await state.set_state(StateMachine.all()[0])  # set admin state
        await message.answer("Вы вошли в режим админа", reply_markup=kb)
    else:
        await message.answer("Эта функция недоступна для вас")


@dp.message_handler(commands=['reservations'], state=StateMachine.ADMIN) # функция вывода календаря для админа
async def reservations(message: types.Message):
    calendar_keyboard = tgcalendar.create_calendar()
    await message.answer("Пожалуйста, выберите дату:", reply_markup=calendar_keyboard)


@dp.message_handler(commands=['stat'], state=StateMachine.ADMIN)  # функция для видов статистики
async def admin_statistics(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Клиенты', callback_data='stat;clients'))
    kb.add(types.InlineKeyboardButton('Время', callback_data='stat;time'))
    await message.answer('Выберите статистику:', reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith('stat'), state=StateMachine.ADMIN) # функция вывода статистики
async def print_stat(callback_query: types.CallbackQuery):
    separated_data = callback_query.data.split(";")
    if separated_data[1] == 'clients':
        for user in db.get_stat_users():
            await bot.send_message(text=user, chat_id=callback_query.message.chat.id)
        await bot.send_message(text=db.get_stat_order(), chat_id=callback_query.message.chat.id)


@dp.message_handler(state=StateMachine.ADMIN_MESSAGE_STATE)  # Отправка рассылки
async def send_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    users = db.get_all_users()
    print(message.content_type)
    for user in users:
        await bot.send_message(text=message.text, chat_id=user['telegram_id'])
    await state.set_state(StateMachine.all()[0])


@dp.message_handler(commands=['send_message'], state=StateMachine.ADMIN)
async def admin_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    await state.set_state(StateMachine.all()[1])
    await bot.send_message(text='Введите сообщение, которое хотите отправить: ', chat_id=message.chat.id)


@dp.message_handler(state=StateMachine.ADMIN)  # функция выхода из режима админа и обработки других сообщений
async def admin_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    if message.text.startswith("Выйти"):
        rm_kb = types.ReplyKeyboardRemove()
        await state.reset_state()  # exit from admin state
        await message.answer("Вы вышли из режима админа", reply_markup=rm_kb)
    else:
        await message.answer("Здарова, админ!")


@dp.message_handler(content_types=['contact'], state=StateMachine.REGISTRATION_PHONE_STATE)  # функции регистрации
async def receive_contact_message(message: types.Message):
    rm_kb = types.ReplyKeyboardRemove()
    state = dp.current_state(user=message.chat.id)
    phone_number = message.contact.phone_number
    print("phone number " + message.contact.phone_number)
    if db.register_new_user(str(await state.get_data()), str(phone_number), str(message.from_user.id)):
        await message.answer('Вы успешно зарегистрировались', reply_markup=rm_kb)
    else:
        await message.answer('Что-то пошло не так :(', reply_markup=rm_kb)
    await state.reset_state()


@dp.message_handler(state=StateMachine.REGISTRATION_NAME_STATE)  # функции регистрации
async def register_message(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(text="Зарегистрироваться", request_contact=True))
    state = dp.current_state(user=message.chat.id)
    name = message.text
    print("register name: " + message.text)
    if name == "" or not name.isalpha():
        await message.answer(f"Вам нужно корректно написать свою фамилию и имя!")
    else:
        await state.set_data(message.text)
        await message.answer(f"Нажмите кнопку ниже, чтобы поделиться с номером телефона", reply_markup=kb)
    await state.set_data(name)
    await state.set_state(StateMachine.all()[5])  # set registration_phone_state


@dp.message_handler(commands=['reserve'])
async def reserve(message: types.Message):
    calendar_keyboard = tgcalendar.create_calendar()
    await message.answer("Пожалуйста, выберите дату:", reply_markup=calendar_keyboard)


@dp.callback_query_handler(lambda c: c.data, state=StateMachine.ADMIN)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['help'])
async def reg(message: types.Message):
    await message.answer("Список команд:\n"
                         "--------------------Обычные команды--------------------\n"
                         "/reg(/start) - зарегистрироваться\n"
                         "/reserve - забронировать стол\n"
                         "-------------------Админские команды-------------------\n"
                         "/admin - войти в режим админа\n"
                         "/reservations - показать все записи на определенную дату\n"
                         "/stat - статистика по клинтам"
                         "Выйти (нажать кнопку под чатом) - выход из режима админа")


@dp.message_handler(commands=['reg', 'start'])
async def reg(message: types.Message):
    telegram_id = message.from_user.id
    if db.is_registered(telegram_id):
        await message.answer(f"Вы уже зарегистрированы")
    else:
        state = dp.current_state(user=message.chat.id)
        await state.set_state(StateMachine.all()[4])  # registration_name_state
        await message.answer("Напишите свое имя")


if __name__ == '__main__':
    executor.start_polling(dp)
