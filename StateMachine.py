from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup


class StateMachine(Helper):
    mode = HelperMode.snake_case

    REGISTRATION_NAME_STATE = ListItem()
    REGISTRATION_PHONE_STATE = ListItem()
    ADMIN = ListItem()
    ADMIN_DELETE_DISH = ListItem()
    ADMIN_NEW_CATEGORY = ListItem()
    PEOPLE_NUMBER = ListItem()
    PEOPLE_TIME = ListItem()
    ADMIN_MESSAGE_STATE = ListItem()


class NewStateMachine(StatesGroup):
    REGISTRATION_NAME_STATE = State()
    REGISTRATION_PHONE_STATE = State()
    ADMIN = State()
    ADMIN_DELETE_DISH = State()
    ADMIN_NEW_CATEGORY = State()
    PEOPLE_NUMBER = State()
    PEOPLE_TIME = State()
    ADMIN_MESSAGE_STATE = State()


if __name__ == '__main__':
    for index, state in enumerate(StateMachine.all()):
        print(f"{index} - {state}")

