from aiogram.utils.helper import Helper, HelperMode, ListItem


class StateMachine(Helper):
    mode = HelperMode.snake_case

    REGISTRATION_NAME_STATE = ListItem()
    REGISTRATION_PHONE_STATE = ListItem()
    ADMIN = ListItem()
    PEOPLE_NUMBER = ListItem()


if __name__ == '__main__':
    print(StateMachine.all())
