

from aiogram.dispatcher import FSMContext

import keyboards

from StateMachine import NewStateMachine
import config
import TGCalendar.telegramcalendar as tgcalendar
from aiogram import Dispatcher, types


async def reserve(message: types.Message):
    calendar_keyboard = tgcalendar.create_calendar()
    await message.answer("Пожалуйста, выберите дату:", reply_markup=calendar_keyboard)


# функция перехода в режим админа
async def set_admin_state(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in config.ADMIN_IDS:
        admin_kb = keyboards.admin_keyboard()
        await state.set_state(NewStateMachine.ADMIN.set())  # set admin state
        await message.answer("Вы вошли в режим админа", reply_markup=admin_kb)
    else:
        await message.answer("Эта функция недоступна для вас")


def register_user_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(set_admin_state, commands=['admin'])
    dp.register_message_handler(reserve, lambda m: m.text.startswith('🪑Забронировать столик'))
    dp.register_message_handler(reserve, commands=['reserve'])

