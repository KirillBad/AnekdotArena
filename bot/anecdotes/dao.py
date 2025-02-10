from database.dao.base import BaseDAO
from anecdotes.model import Anecdote, Rate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


class AnecdoteDAO(BaseDAO):
    model = Anecdote

    @classmethod
    async def find_one_random_not_in(
        cls, session: AsyncSession, exclude_ids: list[int], user_id: int
    ):
        logger.info(
            f"Поиск случайной записи {cls.model.__name__}, исключая ID: {exclude_ids}"
        )
        try:
            query = select(cls.model)
            if exclude_ids:
                query = query.where(cls.model.id.not_in(exclude_ids))
            query = query.where(cls.model.user_id != user_id)
            query = query.order_by(func.random()).limit(1)

            result = await session.execute(query)
            record = result.scalar_one_or_none()

            if record:
                logger.info(f"Случайная запись найдена")
            else:
                logger.info(f"Записи не найдены")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске случайной записи: {e}")
            raise


class RateDAO(BaseDAO):
    model = Rate
