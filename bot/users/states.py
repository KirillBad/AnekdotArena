from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    watching_my_anecdotes = State()
