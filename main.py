import logging
import config
import keyboards as kb
import telegramcalendar as tgcalendar
import spreadsheet
import data
from aiogram import Bot, Dispatcher, executor, types

# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')


@dp.callback_query_handler(lambda c: c.data.startswith('recall'))
async def process_callback_button1(callback_query: types.CallbackQuery):
    if callback_query.data == 'recall_yes':
        data.collect_data('Да', callback_query.from_user.id)
        await bot.send_message(callback_query.from_user.id, 'Отлично, мы вам перезвоним')
    if callback_query.data == 'recall_no':
        data.collect_data('Нет', callback_query.from_user.id)
        await bot.send_message(callback_query.from_user.id, 'Хорошо, приходите на праздник!')
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data.startswith('program'))
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data.collect_data(callback_query.data, callback_query.from_user.id)
    await bot.edit_message_text(text=f'Вы выбрали {callback_query.data[7]} программу',
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, 'Пожалуйста, напишите свой номер телефона')


@dp.callback_query_handler(lambda c: c.data == 'yes' or c.data == 'no')
async def choose_callback(callback_query: types.CallbackQuery):
    if callback_query.data == 'yes':
        await bot.edit_message_text(text=f"Пожалуйста, выберите программу",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=kb.program)
    elif callback_query.data == 'no':
        await bot.edit_message_text(text=f"Ясно!",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    else:
        await bot.edit_message_text(text=f"Что-то пошло не так :(",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    data.collect_data(response[2], callback_query.from_user.id)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['calendar'])
async def calendar(message: types.Message):
    cld = tgcalendar.create_calendar()
    await message.answer('Пожалуйтса, выберите дату:', reply_markup=cld)


@dp.message_handler(lambda c: c.text[0] == '+' or c.text[0] + c.text[1] == '80')
async def test(message: types.Message):
    data.collect_data(message.text, message.from_user.id)
    await message.answer(f'Супер!\n{message.from_user.first_name}, хотите ли вы, чтобы мы вам перезвонили?',
                         reply_markup=kb.recall)


@dp.message_handler(commands=['1'])
async def process_command_1(message: types.Message):
    markup = kb.inline_kb1
    await message.reply("Первая инлайн кнопка", reply_markup=markup)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer("Здарова!\n"
                         "Я тестовый бот\n"
                         "Напиши /calendar чтобы протестировать самую свежую функцию!")


@dp.message_handler(commands=['rm'])
async def removekb(message: types.Message):
    await message.answer('Removed!', reply_markup=kb.ReplyKeyboardRemove())


@dp.message_handler(commands=['ping'])
async def pong(message: types.Message):
    await message.reply('pong')


@dp.message_handler()
async def echo(message: types.Message):
    text = message.text.lower()
    if text.find('пидор') == -1:
        await message.answer(message.text)
    else:
        await message.answer('Сам пидор!')
    print(message.from_user.full_name, message.text)


if __name__ == '__main__':
    executor.start_polling(dp)
