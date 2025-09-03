from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()


class ChangeNameStates(StatesGroup):
    first_name = State()
    last_name = State()


class DriverStates(StatesGroup):
    user_id = State()
    image = State()
    car_brand = State()
    car_number = State()
    license_term = State()
