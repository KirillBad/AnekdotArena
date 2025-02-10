import asyncio
import logging
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import bot, dp
from users.router import user_router
from anecdotes.router import anecdote_router
from payments.router import payments_router
from database.models import *
from database.dao.databae_middleware import (
    DatabaseMiddlewareWithoutCommit,
    DatabaseMiddlewareWithCommit,
)

logging.basicConfig(level=logging.INFO)


async def set_commands():
    commands = [BotCommand(command="start", description="Старт")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main():
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    dp.include_router(user_router)
    dp.include_router(anecdote_router)
    dp.include_router(payments_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
