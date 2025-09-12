from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    taxi_order = State()
    operator = State()


class ChangeNameStates(StatesGroup):
    first_name = State()
    last_name = State()


class DriverStates(StatesGroup):
    id = State()
    image = State()
    car_brand = State()
    car_number = State()
    car_type = State()
    license_term = State()


class DriverUpdateStates(StatesGroup):
    image = State()
    car_brand = State()
    car_number = State()
    license_term = State()


class OrderStates(StatesGroup):
    location = State()
    latitude = State()
    longitude = State()
    order_type = State()
    driver_id = State()
    user_id = State()
