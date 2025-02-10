from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from anecdotes.states import RateStates
from payments.kbs import give_stars_kb
from anecdotes.kbs import rate_anecdote_kb

payments_router = Router()


@payments_router.callback_query(F.data == "give_stars")
async def start_give_stars(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(
        reply_markup=give_stars_kb(),
    )
    await state.set_state(RateStates.selecting_stars_amount)


# @payments_router.callback_query(
#     StarsCallbackFactory.filter(F.action == "give"), RateStates.selecting_stars_amount
# )
# async def process_give_stars(
#     callback: CallbackQuery, callback_data: StarsCallbackFactory, state: FSMContext
# ):
#     await callback.message.edit_reply_markup(
#         reply_markup=give_stars_kb(),
#     )

@payments_router.callback_query(F.data == "back", RateStates.selecting_stars_amount)
async def handle_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RateStates.waiting_for_rate)
    await callback.message.edit_reply_markup(
        reply_markup=rate_anecdote_kb(),
    )