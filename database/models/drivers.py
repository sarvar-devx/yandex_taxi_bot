from sqlalchemy import String, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class Driver(TimeBaseModel):
    image: Mapped[str] = mapped_column(String(255))
    car_brand: Mapped[str] = mapped_column(String(255))
    car_number: Mapped[str] = mapped_column(String(15))
    license_term: Mapped[str] = mapped_column(String(255))
    car_type: Mapped[str] = mapped_column(String(50), nullable=True)
    has_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    has_client: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="driver_profile")
    location: Mapped["DriverLocation"] = relationship("DriverLocation", back_populates="driver", uselist=False)
    orders: Mapped[list["OrderTaxi"]] = relationship("OrderTaxi", back_populates="driver")


class DriverLocation(TimeBaseModel):
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), unique=True)
    driver: Mapped["Driver"] = relationship("Driver", back_populates="location")

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
