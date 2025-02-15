from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    writing_contact_us = State()
    watching_my_anecdotes = State()
    donating_to_prize_fund = State()
