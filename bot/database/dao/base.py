from typing import List, Any, Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from sqlalchemy.future import select
from sqlalchemy import func, delete, update, desc
from pydantic import BaseModel


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись найдена по фильтрам: {filter_dict}")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter_dict}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        logger.info(f"Поиск {cls.model.__name__} с ID: {data_id}")
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с ID {data_id} найдена.")
            else:
                logger.info(f"Запись с ID {data_id} не найдена.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    @classmethod
    async def find_all(cls, session: AsyncSession, filters: BaseModel | None = None, order_by: str | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Поиск всех записей {cls.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            if order_by:
                column = getattr(cls.model, order_by)
                query = query.where(column > 0)
                query = query.order_by(desc(column))
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}"
            )
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Добавление записи {cls.model.__name__} с параметрами: {values_dict}"
        )
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.flush()
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

    @classmethod
    async def count(cls, session: AsyncSession, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Подсчет записей {cls.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(func.count()).select_from(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    async def delete(cls, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {cls.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        try:
            stmt = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            
            if obj:
                await session.delete(obj)
                await session.flush()
                logger.info(f"Запись успешно удалена")
                return 1
            else:
                logger.warning(f"Запись для удаления не найдена")
                return 0
                
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise e
        
    @classmethod
    async def update(cls, session: AsyncSession, values: BaseModel, filters: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        filter_dict = filters.model_dump(exclude_unset=True)

        logger.info(f"Обновление записи {cls.model.__name__} с параметрами: {values_dict}")
        
        try:
            query = (
                update(cls.model)
                .filter_by(**filter_dict)
                .values(**values_dict)
            )
            await session.execute(query)
            await session.flush()
            
            logger.info(f"Запись {cls.model.__name__} успешно обновлена")
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записи: {e}")
            raise
