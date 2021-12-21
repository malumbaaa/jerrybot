from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext


async def cancel_state(callback_query: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.reset_data()
    await callback_query.message.delete()
    await callback_query.message.answer("Действие отменено")


def register_cancel_state_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_state, lambda c: c.data.startswith('cancel_state'), state="*")
