from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards

import db
from StateMachine import NewStateMachine
import TGCalendar.telegramcalendar as tgcalendar
from aiogram import Dispatcher, types


class TableReserveStateMachine(StatesGroup):
    admin_new_category = State()
    people_number = State()
    main_state = State()


async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(callback_query.bot, callback_query)
    print("**"*200)
    await response[0]
    await callback_query.bot.answer_callback_query(callback_query.id)


# функция ввода количества людей
async def table_choose_callback_valid(callback_query: types.CallbackQuery, state: FSMContext):
        separated_data = callback_query.data.split(";")
        date = separated_data[3].split("-")
        await callback_query.answer(callback_query.id)
        await state.set_data(callback_query.data)
        # await state.set_state(NewStateMachine.ADMIN_NEW_CATEGORY.set())  # set people_number state
        await state.set_state(TableReserveStateMachine.people_number)
        await callback_query.message.edit_text(text=f"Вы выбрали "
                                         f"стол №{separated_data[2]} на {separated_data[1]}\n"
                                         f"{date[2]}.{date[1]}.{date[0]}\n"
                                         f"Напишите количество человек:")


# функция ввода количества людей
async def table_choose_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()


# функция для выбора времени
async def people_time_message(callback_query: types.CallbackQuery, state: FSMContext):
    separated_data = callback_query.data.split(";")
    time_kb = keyboards.get_reserved_time(f"{separated_data[2]}-{separated_data[3]}-{separated_data[4]}",
                                          separated_data[1])
    await callback_query.answer()
    await state.set_data(callback_query.data)
    # await state.set_state(NewStateMachine.all()[3])  # set people time set
    await callback_query.message.edit_text(text=f"Выберите время", reply_markup=time_kb)


# функция вывода заказа
async def people_number_message(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        separated_data = str(await state.get_data()).split(";")
        date = separated_data[3].split("-")
        db.reserve_table(separated_data[2], separated_data[3],
                         message.text, separated_data[1], message.from_user.id)
        await state.reset_state()
        await message.answer(f"Вы заказали "
                             f"стол №{separated_data[2]} на {separated_data[1]}\n"
                             f"{date[2]}.{date[1]}.{date[0]}\n"
                             f"на {message.text} человек")
    else:
        await message.answer('Вы ввели некорректное количество людей, повторите ввод')


def register_table_reserve_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(callback_calendar, lambda c: c.data.startswith('IGNORE'))
    dp.register_callback_query_handler(callback_calendar, lambda c: c.data.startswith('PREV-MONTH'))
    dp.register_callback_query_handler(callback_calendar, lambda c: c.data.startswith('DAY'))
    dp.register_callback_query_handler(callback_calendar, lambda c: c.data.startswith('NEXT_MONTH'))
    dp.register_message_handler(people_number_message, state=TableReserveStateMachine.people_number)
    dp.register_callback_query_handler(people_time_message, lambda c: c.data.startswith('table'))
    dp.register_callback_query_handler(table_choose_callback, lambda c: c.data.startswith('reserved'))
    dp.register_callback_query_handler(table_choose_callback_valid, lambda c: c.data.startswith('time'))