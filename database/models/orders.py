from enum import Enum

from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class Order(TimeBaseModel):
    class OrderType(Enum):
        START = "start"
        COMFORT = "comfort"
        BUSINESS = "business"
        PREMIER = "premier"

    class OrderStatus(Enum):
        PENDING = "pending"
        ACCEPTED = "accepted"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    pickup_latitude: Mapped[float] = mapped_column(Float)
    pickup_longitude: Mapped[float] = mapped_column(Float)
    drop_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    drop_longitude: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[SqlAlchemyEnum] = mapped_column(SqlAlchemyEnum(OrderStatus), default=OrderStatus.PENDING)
    type: Mapped[SqlAlchemyEnum] = mapped_column(SqlAlchemyEnum(OrderType), default=OrderType.START)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="orders")
