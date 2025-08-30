from datetime import datetime

import pytz
from sqlalchemy import delete as sqlalchemy_delete, update as sqlalchemy_update, select, func, BigInteger, \
    types
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker, Mapped, mapped_column, selectinload

from config import conf


class Base(AsyncAttrs, DeclarativeBase):

    @declared_attr
    def __tablename__(self) -> str:
        __name = self.__name__[:1]
        for i in self.__name__[1:]:
            if i.isupper():
                __name += '_'
            __name += i
        __name = __name.lower()

        if __name.endswith('y'):
            __name = __name[:-1] + 'ie'
        return __name + 's'


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            conf.db.db_url
        )
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db = AsyncDatabaseSession()
db.init()


class AbstractClass:
    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def create(cls, **kwargs):  # Create
        object_ = cls(**kwargs)
        db.add(object_)
        await cls.commit()
        return object_

    @classmethod
    async def update(cls, id_, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id_)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get(cls, id_):
        query = select(cls).where(cls.id == id_)
        return (await db.execute(query)).scalar()

    @classmethod
    async def delete(cls, id_):
        query = sqlalchemy_delete(cls).where(cls.id == id_)
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def filter(cls, criteria, *, relationship=None):
        query = select(cls).where(criteria)
        if relationship:
            query = query.options(selectinload(relationship))

        return (await db.execute(query)).scalars().all()

    @classmethod
    async def count_by(cls, criteria):
        return (await db.execute(select(func.cSount()).select_from(cls).where(criteria))).scalar()

    @classmethod
    async def all(cls):
        return (await db.execute(select(cls))).scalars().all()


class BaseModel(Base, AbstractClass):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def __str__(self):
        return f"{self.id}"


class TimeStamp(types.TypeDecorator):
    impl = types.DateTime(timezone=True)
    cache_ok = True
    TASHKENT_TIMEZONE = pytz.timezone("Asia/Tashkent")

    def process_bind_param(self, value: datetime, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=pytz.utc)
        return value.astimezone(pytz.utc)

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.astimezone(self.TASHKENT_TIMEZONE)
        return value


class TimeBaseModel(BaseModel):
    __abstract__ = True
    created_at: Mapped[TimeStamp] = mapped_column(TimeStamp, server_default=func.now())
    updated_at: Mapped[TimeStamp] = mapped_column(TimeStamp, server_default=func.now(), server_onupdate=func.now())
