from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import *
from aiogram.types import ParseMode
from StateMachine import StateMachine

import db


@dp.callback_query_handler(lambda c: c.data.startswith('send'), state=NewStateMachine.ADMIN_MESSAGE_STATE)  # Подтверждение рассылки
async def accepted_message(callback_query: types.CallbackQuery):
    separated_data = callback_query.data.split(";")
    users = db.get_all_users()
    state = dp.current_state(user=callback_query.message.chat.id)
    if separated_data[1] == 'go':
        message = await state.get_data()
        message = message['message']
        for user in users:
            await message.send_copy(chat_id=user['telegram_id'])
    elif separated_data[1] == 'reject':
        await callback_query.message.answer(text='Рассылка отменена')
    await state.set_state(NewStateMachine.ADMIN.set())


@dp.message_handler(content_types=types.ContentType.ANY, state=NewStateMachine.ADMIN_MESSAGE_STATE)  # Отправка рассылки
async def send_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    print(message.content_type)
    await state.set_data({'message': message})
    await message.send_copy(chat_id=message.chat.id, reply_markup=keyboards.send_message())