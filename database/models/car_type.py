from enum import Enum
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class CarType(TimeBaseModel):
    class Type(Enum):
        START = 'start'
        COMFORT = 'comfort'
        BUSINESS = 'business'
        PREMIER = 'premier'

    type: Mapped[SqlAlchemyEnum] = mapped_column(SqlAlchemyEnum(Type), default=Type.START)
    price: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)

    drivers: Mapped[list["Driver"]] = relationship("Driver", back_populates="car_type")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="car_type")
