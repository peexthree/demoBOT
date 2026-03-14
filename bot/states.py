from aiogram.fsm.state import State, StatesGroup

class ClientStatesGroup(StatesGroup):
    booking = State()
    faq = State()
    in_twa = State()

class AdminStatesGroup(StatesGroup):
    broadcasting = State()
    analyzing = State()
