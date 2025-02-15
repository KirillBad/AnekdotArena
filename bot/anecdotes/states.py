from aiogram.fsm.state import State, StatesGroup


class AnecdoteStates(StatesGroup):
    waiting_for_text = State()


class RateStates(StatesGroup):
    waiting_for_rate = State()
    selecting_gift = State()
    writing_gift_text = State()
    watching_top_anecdotes = State()
