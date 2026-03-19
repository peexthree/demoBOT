from aiogram.fsm.state import State, StatesGroup

class ClientStatesGroup(StatesGroup):
    booking = State()
    faq = State()
    in_twa = State()

class AdminStatesGroup(StatesGroup):
    broadcasting = State()
    analyzing = State()

class DemoStates(StatesGroup):
    choosing_niche = State()
    in_niche = State()
    waiting_for_photo = State()
    waiting_for_voice = State()
    waiting_for_question = State()
    nps_feedback = State()
    waiting_for_architect_message = State()

class ROICalcStates(StatesGroup):
    waiting_for_leads = State()
    waiting_for_check = State()
