from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from users.utils import get_start_text
from aiogram.fsm.context import FSMContext
from anecdotes.dao import AnecdoteDAO
from users.schemas import TelegramIDModel
from users.dao import UserDAO
from users.states import UserStates
from anecdotes.kbs import PaginationCallbackFactory, back_to_start_kb, pagination_anecdotes_kb
from anecdotes.schemas import AnecdoteUserIdFilter
from config_reader import config
from aiogram.filters.command import Command

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    text, kb = await get_start_text(message, session_with_commit)
    return await message.answer(text, reply_markup=kb)


@user_router.callback_query(F.data == "start")
async def back_to_start(
    callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
):
    await state.clear()
    text, kb = await get_start_text(callback, session_without_commit)
    await callback.message.edit_text(text, reply_markup=kb)


@user_router.callback_query(F.data == "my_anecdotes")
async def my_anecdotes(
    callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
):
    await state.set_state(UserStates.watching_my_anecdotes)

    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=callback.from_user.id),
    )

    my_anecdotes = await AnecdoteDAO.get_anecdotes_with_rating(
        session=session_without_commit, filters=AnecdoteUserIdFilter(user_id=user.id)
    )

    if not my_anecdotes:
        await callback.message.edit_text(
            "У вас пока нет анекдотов", reply_markup=back_to_start_kb()
        )
        return

    serializable_anecdotes = [
        {**record._asdict(), "avg_rating": float(record.avg_rating)}
        for record in my_anecdotes
    ]

    await state.update_data(my_anecdotes=serializable_anecdotes)
    rating = f"{serializable_anecdotes[0]['avg_rating']:.2f}".rstrip("0").rstrip(".")
    await callback.message.edit_text(
        f"{serializable_anecdotes[0]['content']}\n\n📈 Рейтинг: {rating}",
        reply_markup=pagination_anecdotes_kb(1, len(my_anecdotes), "my_anecdotes"),
    )


@user_router.callback_query(
    PaginationCallbackFactory.filter(F.action == "select_page"),
    UserStates.watching_my_anecdotes,
)
async def process_next_my_anecdotes(
    callback: CallbackQuery, callback_data: PaginationCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    my_anecdotes = data.get("my_anecdotes")
    await state.update_data(page=callback_data.page)
    rating = f"{my_anecdotes[callback_data.page - 1]['avg_rating']:.2f}".rstrip(
        "0"
    ).rstrip(".")
    await callback.message.edit_text(
        text=f"{my_anecdotes[callback_data.page - 1]['content']}\n\n📈 Рейтинг: {rating}",
        reply_markup=pagination_anecdotes_kb(
            callback_data.page, len(my_anecdotes), "my_anecdotes"
        ),
    )


@user_router.message(Command("contact_us"))
@user_router.callback_query(F.data == "contact_us")
async def contact_us(event: Message | CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.writing_contact_us)

    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message
    else:
        message = event

    await message.answer(
        text="📝 Отправьте сообщение в чат", reply_markup=back_to_start_kb()
    )


@user_router.message(UserStates.writing_contact_us)
async def process_support_message(
    message: Message, state: FSMContext, session_without_commit: AsyncSession
):
    support_message = (
        f"📨 Новое сообщение в поддержку\n\n"
        f"От: {message.from_user.full_name} ({message.from_user.id})\n"
        f"Username: @{message.from_user.username}\n\n"
        f"Сообщение:\n{message.text}"
    )

    for admin_id in config.ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, support_message)
        except Exception as e:
            print(f"Не удалось отправить сообщение админу {admin_id}: {e}")

    await state.clear()
    text, kb = await get_start_text(message, session_without_commit)
    await message.answer(
        "✅ Спасибо за обращение!\n\nВаше сообщение отправлено команде поддержки.\n"
        "Мы рассмотрим его в ближайшее время."
    )
    await message.answer(text, reply_markup=kb)
