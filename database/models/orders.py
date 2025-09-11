from enum import Enum

from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class Order(TimeBaseModel):
    __tablename__ = "orders"

    class OrderType(Enum):
        START = "start"
        COMFORT = "comfort"
        BUSINESS = "business"
        PREMIER = "premier"

    class OrderStatus(Enum):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DRIVER_GOING = "driver_going"      # Haydovchi kelmoqda
        DRIVER_ARRIVED = "driver_arrived"  # Haydovchi yetib keldi
        IN_PROGRESS = "in_progress"        # Safar boshlandi
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

    # Address relationships - to'g'ri sintaks
    pickup_address: Mapped["Address"] = relationship(
        "Address",
        foreign_keys="Order.pickup_address_id",
        back_populates="pickup_orders"
    )
    destination_address: Mapped["Address"] = relationship(
        "Address",
        foreign_keys="Order.destination_address_id",
        back_populates="destination_orders"
    )

    # Address relationship orqali manzillarcl
    pickup_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    destination_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=True)

    # Narx ma'lumotlari
    estimated_price: Mapped[float] = mapped_column(Float, default=0.0)
    final_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=True)
    toll_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=True)
    waiting_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=True)
