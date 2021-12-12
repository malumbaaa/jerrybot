import json
import logging

from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import bold

from handlers.admin.adding_dishes import register_handlers_food, AddDish
import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ParseMode
import keyboards
from handlers.user.menu_handler import register_handlers_menu, Menu
from handlers.user.user_menu_handler import register_user_handlers_menu
from handlers.common.registration_handler import register_common_handlers
from handlers.user.table_reserve_handler import register_table_reserve_handlers
from handlers.admin.admin_menu_handler import register_admin_menu_handlers
from handlers.admin.delete_dish_handler import register_delete_dish_admin
from handlers.admin.sendings_handler import register_sending_handlers
from handlers.admin.statistics_handler import register_statistics_handlers

import db
from StateMachine import NewStateMachine, StateMachine
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


# @dp.message_handler(state=NewStateMachine.PEOPLE_NUMBER)  # функция вывода заказа
# async def people_number_message(message: types.Message):
#     if message.text.isdigit():
#         state = dp.current_state(user=message.chat.id)
#         separated_data = str(await state.get_data()).split(";")
#         date = separated_data[3].split("-")
#         db.reserve_table(separated_data[2], separated_data[3],
#                          message.text, separated_data[1], message.from_user.id)
#         await state.reset_state()
#         await message.answer(f"Вы заказали "
#                              f"стол №{separated_data[2]} на {separated_data[1]}\n"
#                              f"{date[2]}.{date[1]}.{date[0]}\n"
#                              f"на {message.text} человек")
#     else:
#         await message.answer('Вы ввели некорректное количество людей, повторите ввод')


# @dp.callback_query_handler(lambda c: c.data.startswith('table'))  # функция для выбора времени
# async def people_time_message(callback_query: types.CallbackQuery):
#     state = dp.current_state(user=callback_query.message.chat.id)
#     separated_data = callback_query.data.split(";")
#     time_kb = keyboards.get_reserved_time(f"{separated_data[2]}-{separated_data[3]}-{separated_data[4]}",
#                                           separated_data[1])
#     await bot.answer_callback_query(callback_query.id)
#     await state.set_data(callback_query.data)
#     # await state.set_state(NewStateMachine.all()[3])  # set people time set
#     await bot.edit_message_text(text=f"Выберите время", reply_markup=time_kb, chat_id=callback_query.message.chat.id,
#                                 message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data.startswith('DAY'), state=NewStateMachine.ADMIN) # функция вывода заказанных столов и админа
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


# @dp.callback_query_handler(lambda c: c.data.startswith('reserved'))  # функция ввода количества людей
# async def table_choose_callback(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)


# @dp.callback_query_handler(lambda c: c.data.startswith('time'))  # функция ввода количества людей
# async def table_choose_callback(callback_query: types.CallbackQuery):
#     state = dp.current_state(user=callback_query.message.chat.id)
#     separated_data = callback_query.data.split(";")
#     date = separated_data[3].split("-")
#     await bot.answer_callback_query(callback_query.id)
#     await state.set_data(callback_query.data)
#     await state.set_state(NewStateMachine.ADMIN_NEW_CATEGORY.set())  # set people_number state
#     await bot.edit_message_text(text=f"Вы выбрали "
#                                      f"стол №{separated_data[2]} на {separated_data[1]}\n"
#                                      f"{date[2]}.{date[1]}.{date[0]}\n"
#                                      f"Напишите количество человек:",
#                                 chat_id=callback_query.message.chat.id,
#                                 message_id=callback_query.message.message_id)


# @dp.message_handler(commands=['admin'])  # функция перехода в режим админа
# async def set_admin_state(message: types.Message):
#     if str(message.from_user.id) in config.ADMIN_IDS:
#         state = dp.current_state(user=message.chat.id)
#         admin_kb = keyboards.admin_keyboard()
#         await state.set_state(NewStateMachine.ADMIN.set())  # set admin state
#         await message.answer("Вы вошли в режим админа", reply_markup=admin_kb)
#     else:
#         await message.answer("Эта функция недоступна для вас")


@dp.message_handler(lambda m: m.text.startswith('Test Qr-Code'), state=NewStateMachine.ADMIN)
async def test_qr_code(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фотографию с QR кодом")
    await Menu.qr_scan.set()


@dp.message_handler(commands=['reservations'], state=NewStateMachine.ADMIN) # функция вывода календаря для админа
async def reservations(message: types.Message):
    calendar_keyboard = tgcalendar.create_calendar()
    await message.answer("Пожалуйста, выберите дату:", reply_markup=calendar_keyboard)


@dp.message_handler(state=NewStateMachine.ADMIN_NEW_CATEGORY)
async def category_message(message: types.Message):
    db.add_category(message.text)
    state = dp.current_state(user=message.chat.id)
    await state.set_state(AddDish.waiting_for_dish_name)
    await state.update_data(category=message.text)
    await message.answer(f"Категория {message.text} добавлена\nНапишите название блюда",
                         reply_markup=types.ReplyKeyboardRemove())


# @dp.callback_query_handler(lambda c: c.data.startswith('category'), state=NewStateMachine.ADMIN_DELETE_DISH)
# async def category_delete_dish_callback(callback_query: types.CallbackQuery):
#     separated_data = callback_query.data.split(";")
#     state = dp.current_state(user=callback_query.message.chat.id)
#     food = db.get_food_by_category(separated_data[1])
#     kb = keyboards.beautiful_change_of_food(0, len(food), separated_data[1], food[0]['name'], 'delete')
#     try:
#         await callback_query.message.answer_photo(photo=food[0]['photo_id'],
#                                                   caption=bold(f"{food[0]['name']}\n\n") +
#                                                           f"{food[0]['description']}\n\n" +
#                                                           bold(f"{food[0]['price']} BYN\n"),
#                                                   parse_mode=ParseMode.MARKDOWN,
#                                                   reply_markup=kb)
#         await callback_query.answer()
#     except IndexError:
#         await callback_query.message.answer(text="В этой категории нет еды")


@dp.callback_query_handler(lambda c: c.data.startswith('category'), state=NewStateMachine.ADMIN)
async def category_callback(callback_query: types.CallbackQuery):
    separated_data = callback_query.data.split(";")
    state = dp.current_state(user=callback_query.message.chat.id)
    if separated_data[1] == "addnew":
        await state.set_state(NewStateMachine.ADMIN_NEW_CATEGORY.set())  # admin_new_category state
        await bot.edit_message_text(text="Напишите название категории",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        await bot.answer_callback_query(callback_query.id)
    else:
        await state.set_state(AddDish.waiting_for_dish_name)
        await state.update_data(category=separated_data[1])
        await bot.edit_message_text(text=f"Категория: {separated_data[1]}\nНапишите название блюда",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        await bot.answer_callback_query(callback_query.id)


# @dp.message_handler(lambda m: m.text.startswith('❌Выйти из режима удаления❌'), state=NewStateMachine.ADMIN_DELETE_DISH)
# # @dp.callback_query_handler(lambda c: c.data.startswith('exitDeletion'), state=NewStateMachine.ADMIN_DELETE_DISH)
# async def exit_delete_dish(message: types.Message):
#     state = dp.current_state(user=message.chat.id)
#     await state.set_state(NewStateMachine.ADMIN.state())  # set admin state
#     admin_kb = keyboards.admin_keyboard()
#     await message.answer("Вы вышли из режима удаления", reply_markup=admin_kb)


# @dp.callback_query_handler(lambda c: c.data.startswith('delete'), state=NewStateMachine.ADMIN_DELETE_DISH)
# async def delete_dish(callback_query: types.CallbackQuery):
#     separated_data = callback_query.data.split(';')
#     name = separated_data[1]
#     db.delete_food_by_name(name)
#     exit_deletion_markup = InlineKeyboardMarkup(row_width=1)
#     exit_btn = InlineKeyboardButton("Выйти из режима удаления", callback_data=f"exitDeletion")
#     exit_deletion_markup.add(exit_btn)
#     await callback_query.message.answer(f"Блюдо {name} удалено", reply_markup=exit_deletion_markup)


# @dp.callback_query_handler(lambda c: c.data.startswith('food'), state=NewStateMachine.ADMIN_DELETE_DISH)
# async def change_delete_food_by_callback(callback_query: types.CallbackQuery):
#     categories = callback_query.data.split(';')
#     food = db.get_food_by_category(categories[1])
#     current_food = int(categories[2])
#     if len(food) > current_food >= 0:
#         try:
#             next_photo = types.input_media.InputMediaPhoto(str='photo', media=food[current_food]['photo_id'],
#                                                            caption=bold(f"{food[current_food]['name']}\n\n") +
#                                                               f"{food[current_food]['description']}\n\n" +
#                                                               bold(f"{food[current_food]['price']} BYN\n"),
#                                                            parse_mode=ParseMode.MARKDOWN)
#             await callback_query.message.edit_media(media=next_photo,
#                                                     reply_markup=keyboards
#                                                    .beautiful_change_of_food(current_food,
#                                                                              len(food),
#                                                                              categories[1],
#                                                                              food[current_food]['name'], 'delete'))
#             await callback_query.answer()
#         except:
#             await callback_query.answer()
#     else:
#         await callback_query.answer()


# @dp.message_handler(lambda m: m.text.startswith('🗑Удалить блюдо🗑'), state=NewStateMachine.ADMIN)
# @dp.message_handler(commands=['delete'], state=NewStateMachine.ADMIN)
# async def delete_dish(message: types.Message):
#     state = dp.current_state(user=message.chat.id)
#     await state.set_state(NewStateMachine.ADMIN_DELETE_DISH.set())
#     deletion_kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     deletion_kb.add(types.KeyboardButton(text="❌Выйти из режима удаления❌"))
#     await message.answer("Режим удаления блюд", reply_markup=deletion_kb)
#     kb = keyboards.get_categories_kb()
#     await message.answer('Выберите категорию:', reply_markup=kb)


# @dp.message_handler(lambda m: m.text.startswith('🍽Добавить блюдо🍽'), state=NewStateMachine.ADMIN)
# @dp.message_handler(commands=['add'], state=NewStateMachine.ADMIN)
# async def add_dish(message: types.Message):
#     kb = keyboards.get_categories_kb()
#     kb.add(types.InlineKeyboardButton('Создать новую', callback_data='category;addnew'))
#     await message.answer('Выберите категорию:', reply_markup=kb)


# @dp.message_handler(lambda m: m.text.startswith('📊Посмотреть статистику'), state=NewStateMachine.ADMIN)
# @dp.message_handler(commands=['stat'], state=NewStateMachine.ADMIN)  # функция для видов статистики
# async def admin_statistics(message: types.Message):
#     kb = InlineKeyboardMarkup()
#     kb.add(types.InlineKeyboardButton('Клиенты', callback_data='stat;clients'))
#     kb.add(types.InlineKeyboardButton('Время', callback_data='stat;time'))
#     kb.add(types.InlineKeyboardButton('Заказы', callback_data='stat;orders'))
#     await message.answer('Выберите статистику:', reply_markup=kb)


# @dp.callback_query_handler(lambda c: c.data.startswith('stat'), state=NewStateMachine.ADMIN) # функция вывода статистики
# async def print_stat(callback_query: types.CallbackQuery):
#     separated_data = callback_query.data.split(";")
#     if separated_data[1] == 'clients':
#         db.get_stat_users()
#         clients= types.input_file.InputFile("clients.xlsx")
#         await bot.send_document(document=clients, chat_id=callback_query.message.chat.id)
#         all_days = types.input_file.InputFile("all_days.png")
#         await bot.send_photo(caption=db.get_stat_order(), chat_id=callback_query.message.chat.id, photo=all_days)
#     if separated_data[1] == 'time':
#         messages = db.get_stat_time()
#         for key, value in messages[0].items():
#             caption = f"{key}\nВремя\tЗаказы\tЛюди\n"
#             for time, text in value.items():
#                 caption += f"{time}\t\t\t  {text}\t\t\t         {messages[1][key][time]}\n"
#             day = types.input_file.InputFile(f"{key}.png")
#             await bot.send_photo(photo=day, chat_id=callback_query.message.chat.id, caption=caption)
#     if separated_data[1] == 'orders':
#         await callback_query.message.answer(text="Выберите столик по которому хотите получить статистику",
#                                             reply_markup=keyboards.table_choose(5, 2021, 10, 24))


# @dp.callback_query_handler(lambda c: c.data.startswith('table'), state=NewStateMachine.ADMIN)
# async def print_order_stat(callback_query: types.CallbackQuery):
#     separated_date = callback_query.data.split(';')
#     db.stat_tables(int(separated_date[1]))
#     orders = types.input_file.InputFile("orders.xlsx")
#     await bot.send_document(document=orders, chat_id=callback_query.message.chat.id)


# @dp.message_handler(content_types=types.ContentType.ANY, state=NewStateMachine.ADMIN_MESSAGE_STATE)  # Отправка рассылки
# async def send_message(message: types.Message):
#     state = dp.current_state(user=message.chat.id)
#     print(message.content_type)
#     await state.set_data({'message': message})
#     await message.send_copy(chat_id=message.chat.id, reply_markup=keyboards.send_message())


# @dp.callback_query_handler(lambda c: c.data.startswith('send'), state=NewStateMachine.ADMIN_MESSAGE_STATE)  # Подтверждение рассылки
# async def accepted_message(callback_query: types.CallbackQuery):
#     separated_data = callback_query.data.split(";")
#     users = db.get_all_users()
#     state = dp.current_state(user=callback_query.message.chat.id)
#     if separated_data[1] == 'go':
#         message = await state.get_data()
#         message = message['message']
#         for user in users:
#             await message.send_copy(chat_id=user['telegram_id'])
#     elif separated_data[1] == 'reject':
#         await callback_query.message.answer(text='Рассылка отменена')
#     await state.set_state(NewStateMachine.ADMIN.set())


# @dp.message_handler(lambda m: m.text.startswith('✉Отправить рассылку'), state=NewStateMachine.ADMIN)
# @dp.message_handler(commands=['send_message'], state=NewStateMachine.ADMIN)
# async def admin_message(message: types.Message):
#     state = dp.current_state(user=message.chat.id)
#     await state.set_state(NewStateMachine.ADMIN_MESSAGE_STATE.set())
#     await bot.send_message(text='Введите сообщение, которое хотите отправить: ', chat_id=message.chat.id)


# @dp.message_handler(state=NewStateMachine.ADMIN)  # функция выхода из режима админа и обработки других сообщений
# async def admin_message(message: types.Message):
#     state = dp.current_state(user=message.chat.id)
#     if message.text.startswith("❌Выйти"):
#         rm_kb = types.ReplyKeyboardRemove()
#         kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         kb.add(types.KeyboardButton(text="🍽Меню🍽"))
#         kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
#         await state.reset_state()  # exit from admin state
#         await message.answer("Вы вышли из режима админа", reply_markup=kb)
#     else:
#         print(message.content_type)
#         await message.answer("Здарова, админ!")


# @dp.message_handler(content_types=['contact'], state=NewStateMachine.REGISTRATION_PHONE_STATE)  # функции регистрации
# async def receive_contact_message(message: types.Message):
#     rm_kb = types.ReplyKeyboardRemove()
#     state = dp.current_state(user=message.chat.id)
#     phone_number = message.contact.phone_number
#     kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     kb.add(types.KeyboardButton(text="🍽Меню🍽"))
#     kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
#     print("phone number " + message.contact.phone_number)
#     if db.register_new_user(str(await state.get_data()), str(phone_number), str(message.from_user.id)):
#         await message.answer('Вы успешно зарегистрировались', reply_markup=kb)
#     else:
#         await message.answer('Что-то пошло не так :(', reply_markup=rm_kb)
#     await state.reset_state()


# @dp.message_handler(state=NewStateMachine.REGISTRATION_NAME_STATE)  # функции регистрации
# async def register_message(message: types.Message):
#     kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     kb.add(types.KeyboardButton(text="Зарегистрироваться", request_contact=True))
#     state = dp.current_state(user=message.chat.id)
#     name = message.text
#     print("register name: " + message.text)
#     if name == "" or not name.isalpha():
#         await message.answer(f"Вам нужно корректно написать свою фамилию и имя!")
#     else:
#         await state.set_data(message.text)
#         await message.answer(f"Нажмите кнопку ниже, чтобы поделиться с номером телефона", reply_markup=kb)
#     await state.set_data(name)
#     await state.set_state(NewStateMachine.REGISTRATION_PHONE_STATE.set())  # set registration_phone_state


# @dp.message_handler(lambda m: m.text.startswith('🪑Забронировать столик'))
# @dp.message_handler(commands=['reserve'])
# async def reserve(message: types.Message):
#     calendar_keyboard = tgcalendar.create_calendar()
#     await message.answer("Пожалуйста, выберите дату:", reply_markup=calendar_keyboard)


@dp.callback_query_handler(lambda c: c.data, state=NewStateMachine.ADMIN)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


# @dp.callback_query_handler(lambda c: c.data.startswith('IGNORE'))
# @dp.callback_query_handler(lambda c: c.data.startswith('PREV-MONTH'))
# @dp.callback_query_handler(lambda c: c.data.startswith('DAY'))
# @dp.callback_query_handler(lambda c: c.data.startswith('NEXT-MONTH'))
# async def callback_calendar(callback_query: types.CallbackQuery):
#     response = tgcalendar.process_calendar_selection(bot, callback_query)
#     await response[0]
#     await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['help'])
async def reg(message: types.Message):
    await message.answer("Список команд:\n"
                         "--------------------Обычные команды--------------------\n"
                         "/reg(/start) - зарегистрироваться\n"
                         "/reserve - забронировать стол\n"
                         "-------------------Админские команды-------------------\n"
                         "/admin - войти в режим админа\n"
                         "/reservations - показать все записи на определенную дату\n"
                         "/stat - статистика по клиентам"
                         "Выйти (нажать кнопку под чатом) - выход из режима админа")


# @dp.message_handler(commands=['reg', 'start'])
# async def reg(message: types.Message):
#     telegram_id = message.from_user.id
#     if db.is_registered(telegram_id):
#         state = dp.current_state(user=message.chat.id)
#         kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         kb.add(types.KeyboardButton(text="🍽Меню🍽"))
#         kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
#         await message.answer(f"Вы уже зарегистрированы", reply_markup=kb)
#     else:
#         state = dp.current_state(user=message.chat.id)
#         await state.set_state(NewStateMachine.REGISTRATION_PHONE_STATE.set())  # registration_name_state
#         await message.answer("Напишите свое имя")


if __name__ == '__main__':
    register_handlers_menu(dp)
    register_handlers_food(dp)
    register_user_handlers_menu(dp)
    register_common_handlers(dp)
    register_table_reserve_handlers(dp)
    register_admin_menu_handlers(dp)
    register_delete_dish_admin(dp)
    register_sending_handlers(dp)
    register_statistics_handlers(dp)
    executor.start_polling(dp)

# исправить в админке всё, кроме эдинг дишес и меню

