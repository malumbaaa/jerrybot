from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

buttonHi = KeyboardButton('Привет!!')
buttonRm = KeyboardButton('/rm')
buttontest1 = KeyboardButton('Test1')
buttontest2 = KeyboardButton('Test2')

kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.row(buttonHi, buttonRm)
kb.add(buttontest1, buttontest2)

inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

program1_btn = InlineKeyboardButton('Первая программа', callback_data='program1')
program2_btn = InlineKeyboardButton('Вторая программа', callback_data='program2')
program3_btn = InlineKeyboardButton('Третья программа', callback_data='program3')
program4_btn = InlineKeyboardButton('Четвертая программа', callback_data='program4')
program5_btn = InlineKeyboardButton('Первая программа', callback_data='program5')
program = InlineKeyboardMarkup(row_width=1)
program.row(program1_btn)
program.row(program2_btn)
program.row(program3_btn)
program.row(program4_btn)
program.row(program5_btn)

recall_yes = InlineKeyboardButton('Да', callback_data='recall_yes')
recall_no = InlineKeyboardButton('Нет', callback_data='recall_no')
recall = InlineKeyboardMarkup(row_width=2)
recall.row(recall_yes, recall_no)
