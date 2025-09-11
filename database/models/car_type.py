from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class CarType(TimeBaseModel):
    __tablename__ = "car_types"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)

    drivers: Mapped[list["Driver"]] = relationship("Driver", back_populates="car_type")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="car_type")



