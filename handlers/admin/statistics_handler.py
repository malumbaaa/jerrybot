import keyboards

import db
from StateMachine import NewStateMachine
from aiogram import Dispatcher, types


# функция вывода статистики
async def print_stat(callback_query: types.CallbackQuery):
    separated_data = callback_query.data.split(";")
    if separated_data[1] == 'clients':
        db.get_stat_users()
        clients= types.input_file.InputFile("clients.xlsx")
        await callback_query.bot.send_document(document=clients, chat_id=callback_query.message.chat.id)
        all_days = types.input_file.InputFile("all_days.png")
        await callback_query.bot.send_photo(caption=db.get_stat_order(), chat_id=callback_query.message.chat.id, photo=all_days)
    if separated_data[1] == 'time':
        messages = db.get_stat_time()
        for key, value in messages[0].items():
            caption = f"{key}\nВремя\tЗаказы\tЛюди\n"
            for time, text in value.items():
                caption += f"{time}\t\t\t  {text}\t\t\t         {messages[1][key][time]}\n"
            day = types.input_file.InputFile(f"{key}.png")
            await callback_query.bot.send_photo(photo=day, chat_id=callback_query.message.chat.id, caption=caption)
    if separated_data[1] == 'orders':
        await callback_query.message.answer(text="Выберите столик по которому хотите получить статистику",
                                            reply_markup=keyboards.table_choose(5, 2021, 10, 24))


async def print_order_stat(callback_query: types.CallbackQuery):
    separated_date = callback_query.data.split(';')
    db.stat_tables(int(separated_date[1]))
    orders = types.input_file.InputFile("orders.xlsx")
    await callback_query.bot.send_document(document=orders, chat_id=callback_query.message.chat.id)


def register_statistics_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(print_order_stat, lambda c: c.data.startswith('table'),
                                       state=NewStateMachine.ADMIN)
    dp.register_callback_query_handler(print_stat, lambda c: c.data.startswith('stat'), state=NewStateMachine.ADMIN)
