from aiogram.dispatcher import FSMContext

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ParseMode
import keyboards

from StateMachine import NewStateMachine
from aiogram import Bot, Dispatcher, executor, types


async def admin_sending(message: types.Message, state: FSMContext):
    await state.set_state(NewStateMachine.ADMIN_MESSAGE_STATE.set())
    await message.bot.send_message(text='Введите сообщение, которое хотите отправить: ', chat_id=message.chat.id)


async def add_dish(message: types.Message):
    kb = keyboards.get_categories_kb()
    kb.add(types.InlineKeyboardButton('Создать новую', callback_data='category;addnew'))
    await message.answer('Выберите категорию:', reply_markup=kb)


async def delete_dish(message: types.Message, state: FSMContext):
    await state.set_state(NewStateMachine.ADMIN_DELETE_DISH.set())
    deletion_kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    deletion_kb.add(types.KeyboardButton(text="❌Выйти из режима удаления❌"))
    await message.answer("Режим удаления блюд", reply_markup=deletion_kb)
    kb = keyboards.get_categories_kb()
    await message.answer('Выберите категорию:', reply_markup=kb)


# функция выхода из режима админа и обработки других сообщений
async def admin_message(message: types.Message, state: FSMContext):
    if message.text.startswith("❌Выйти"):
        rm_kb = types.ReplyKeyboardRemove()
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton(text="🍽Меню🍽"))
        kb.add(types.KeyboardButton(text="🪑Забронировать столик🪑"))
        await state.reset_state()  # exit from admin state
        await message.answer("Вы вышли из режима админа", reply_markup=kb)
    else:
        print(message.content_type)
        await message.answer("Здарова, админ!")


# функция для видов статистики
async def admin_statistics(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Клиенты', callback_data='stat;clients'))
    kb.add(types.InlineKeyboardButton('Время', callback_data='stat;time'))
    kb.add(types.InlineKeyboardButton('Заказы', callback_data='stat;orders'))
    await message.answer('Выберите статистику:', reply_markup=kb)


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_statistics, commands=['stat'], state=NewStateMachine.ADMIN)
    dp.register_message_handler(admin_statistics, lambda m: m.text.startswith('📊Посмотреть статистику'),
                                state=NewStateMachine.ADMIN)
    dp.register_message_handler(admin_message, state=NewStateMachine.ADMIN)
    dp.register_message_handler(delete_dish, commands=['delete'], state=NewStateMachine.ADMIN)
    dp.register_message_handler(delete_dish, lambda m: m.text.startswith('🗑Удалить блюдо🗑'),
                                state=NewStateMachine.ADMIN)
    dp.register_message_handler(add_dish, commands=['add'], state=NewStateMachine.ADMIN)
    dp.register_message_handler(add_dish, lambda m: m.text.startswith('🍽Добавить блюдо🍽'), state=NewStateMachine.ADMIN)
    dp.register_message_handler(admin_sending, commands=['send_message'], state=NewStateMachine.ADMIN)
    dp.register_message_handler(admin_sending, lambda m: m.text.startswith('✉Отправить рассылку'),
                                state=NewStateMachine.ADMIN)
