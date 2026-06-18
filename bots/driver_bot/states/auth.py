from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_login = State()
    waiting_password = State()
    
class RegisterStates(StatesGroup):
    waiting_full_name = State()
    waiting_phone = State()
    waiting_car_model = State()
    waiting_car_color = State()
    waiting_car_number = State()
    waiting_password = State()