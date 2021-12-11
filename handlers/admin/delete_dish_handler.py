from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import *
from aiogram.types import ParseMode
from StateMachine import StateMachine

import db


@dp.callback_query_handler(lambda c: c.data.startswith('category'), state=NewStateMachine.ADMIN_DELETE_DISH)
async def category_delete_dish_callback(callback_query: types.CallbackQuery):
    separated_data = callback_query.data.split(";")
    state = dp.current_state(user=callback_query.message.chat.id)
    food = db.get_food_by_category(separated_data[1])
    kb = keyboards.beautiful_change_of_food(0, len(food), separated_data[1], food[0]['name'], 'delete')
    try:
        await callback_query.message.answer_photo(photo=food[0]['photo_id'],
                                                  caption=bold(f"{food[0]['name']}\n\n") +
                                                          f"{food[0]['description']}\n\n" +
                                                          bold(f"{food[0]['price']} BYN\n"),
                                                  parse_mode=ParseMode.MARKDOWN,
                                                  reply_markup=kb)
        await callback_query.answer()
    except IndexError:
        await callback_query.message.answer(text="В этой категории нет еды")


@dp.callback_query_handler(lambda c: c.data.startswith('food'), state=NewStateMachine.ADMIN_DELETE_DISH)
async def change_delete_food_by_callback(callback_query: types.CallbackQuery):
    categories = callback_query.data.split(';')
    food = db.get_food_by_category(categories[1])
    current_food = int(categories[2])
    if len(food) > current_food >= 0:
        try:
            next_photo = types.input_media.InputMediaPhoto(str='photo', media=food[current_food]['photo_id'],
                                                           caption=bold(f"{food[current_food]['name']}\n\n") +
                                                              f"{food[current_food]['description']}\n\n" +
                                                              bold(f"{food[current_food]['price']} BYN\n"),
                                                           parse_mode=ParseMode.MARKDOWN)
            await callback_query.message.edit_media(media=next_photo,
                                                    reply_markup=keyboards
                                                   .beautiful_change_of_food(current_food,
                                                                             len(food),
                                                                             categories[1],
                                                                             food[current_food]['name'], 'delete'))
            await callback_query.answer()
        except:
            await callback_query.answer()
    else:
        await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('delete'), state=NewStateMachine.ADMIN_DELETE_DISH)
async def delete_dish(callback_query: types.CallbackQuery):
    separated_data = callback_query.data.split(';')
    name = separated_data[1]
    db.delete_food_by_name(name)
    exit_deletion_markup = InlineKeyboardMarkup(row_width=1)
    exit_btn = InlineKeyboardButton("Выйти из режима удаления", callback_data=f"exitDeletion")
    exit_deletion_markup.add(exit_btn)
    await callback_query.message.answer(f"Блюдо {name} удалено", reply_markup=exit_deletion_markup)


@dp.message_handler(lambda m: m.text.startswith('❌Выйти из режима удаления❌'), state=NewStateMachine.ADMIN_DELETE_DISH)
# @dp.callback_query_handler(lambda c: c.data.startswith('exitDeletion'), state=NewStateMachine.ADMIN_DELETE_DISH)
async def exit_delete_dish(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    await state.set_state(NewStateMachine.ADMIN.state())  # set admin state
    admin_kb = keyboards.admin_keyboard()
    await message.answer("Вы вышли из режима удаления", reply_markup=admin_kb)