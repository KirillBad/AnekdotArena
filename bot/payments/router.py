from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from anecdotes.states import RateStates
from payments.kbs import give_stars_kb
from anecdotes.kbs import rate_anecdote_kb
from payments.kbs import GiveStarsCallbackFactory

payments_router = Router()


@payments_router.callback_query(F.data == "select_stars")
async def start_give_stars(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RateStates.selecting_stars_amount)
    await callback.message.edit_reply_markup(
        reply_markup=give_stars_kb(),
    )

@payments_router.callback_query(
    GiveStarsCallbackFactory.filter(F.action == "stars"), RateStates.selecting_stars_amount
)
async def process_give_stars(
    callback: CallbackQuery, callback_data: GiveStarsCallbackFactory, state: FSMContext
):
    await callback.message.reply_invoice(
        title="Задонатить автору анекдота",
        description="Автор получит подарок на сумму эквивалентную количеству звезд (подарок можно сконвертировать в ⭐️ при получении) за вычетом комиссии 10%",
        payload="test",
        provider_token="",
        prices=[LabeledPrice(label="XTR", amount=callback_data.value)],
        currency="XTR",
    )

@payments_router.callback_query(F.data == "back", RateStates.selecting_stars_amount)
async def handle_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RateStates.waiting_for_rate)
    await callback.message.edit_reply_markup(
        reply_markup=rate_anecdote_kb(),
    )