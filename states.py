from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    full_name = State()
    phone = State()
    location = State()

class AddHospitalState(StatesGroup):
    name = State()
    address = State()

class AddDoctorState(StatesGroup):
    name = State()
    specialty = State()
    available_times = State()
    hospital_id = State()