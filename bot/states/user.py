from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()


class ChangeNameStates(StatesGroup):
    first_name = State()
    last_name = State()
