from database.dao.base import BaseDAO
from anecdotes.model import Anecdote, Rate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select, desc
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

    @classmethod
    async def get_top_anecdotes(cls, session: AsyncSession):
        logger.info(f"Получение топ анекдотов")
        try:
            query = (
                select(
                    cls.model.anecdote_id,
                    Anecdote.content,
                    Anecdote.user_id,
                    func.avg(cls.model.rating).label('avg_rating'),
                )
                .join(Anecdote, cls.model.anecdote_id == Anecdote.id)
                .group_by(cls.model.anecdote_id, Anecdote.content, Anecdote.user_id)
                .order_by(desc('avg_rating')).limit(10)
            )
            
            result = await session.execute(query)
            records = result.all()
            
            logger.info(f"Найдено {len(records)} анекдотов для топа")
            return records
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении топ анекдотов: {e}")
            raise
