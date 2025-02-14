from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    watching_reports = State()
