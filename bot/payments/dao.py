from database.dao.base import BaseDAO
from payments.models import Gift, Donation
from database.dao.base import BaseDAO
from payments.models import Donation
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from loguru import logger


class GiftDAO(BaseDAO):
    model = Gift


class DonationDAO(BaseDAO):
    model = Donation

    @classmethod
    async def sum_amount(cls, session: AsyncSession, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Подсчет суммы amount в {cls.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(func.sum(cls.model.amount)).filter_by(**filter_dict)
            result = await session.execute(query)
            total = result.scalar() or 0
            logger.info(f"Общая сумма: {total}")
            return total
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете суммы по фильтрам {filter_dict}: {e}")
            raise
