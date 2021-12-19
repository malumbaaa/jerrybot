from aiogram.dispatcher import FSMContext
import keyboards


import db
from StateMachine import NewStateMachine
from aiogram import Dispatcher,  types
from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminSendMessageStateMachine(StatesGroup):
    admin_message_state = State()


 # Подтверждение рассылки
async def accepted_message(callback_query: types.CallbackQuery, state: FSMContext):
    separated_data = callback_query.data.split(";")
    users = db.get_all_users()
    if separated_data[1] == 'go':
        message = await state.get_data()
        message = message['message']
        for user in users:
            await message.send_copy(chat_id=user['telegram_id'])
    elif separated_data[1] == 'reject':
        await callback_query.message.answer(text='Рассылка отменена')
    await state.set_state(NewStateMachine.ADMIN)


  # Отправка рассылки
async def send_message(message: types.Message, state: FSMContext):
    print(message.content_type)
    await state.set_data({'message': message})
    await message.send_copy(chat_id=message.chat.id, reply_markup=keyboards.send_message())


def register_sending_handlers(dp: Dispatcher):
    dp.register_message_handler(send_message, content_types=types.ContentType.ANY,
                                state=AdminSendMessageStateMachine.admin_message_state)
    dp.register_callback_query_handler(accepted_message, lambda c: c.data.startswith('send'),
                              state=AdminSendMessageStateMachine.admin_message_state)