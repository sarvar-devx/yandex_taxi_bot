from datetime import datetime

from sqlalchemy import Integer, DateTime
from sqlalchemy import String, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class Driver(TimeBaseModel):
    image: Mapped[str] = mapped_column(String(255))
    car_brand: Mapped[str] = mapped_column(String(255))
    car_number: Mapped[str] = mapped_column(String(15))
    license_term: Mapped[str] = mapped_column(String(255))
    has_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    has_client: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="driver_profile")
    location: Mapped["DriverLocation"] = relationship("DriverLocation", back_populates="driver", uselist=False)
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="driver")
    comments = relationship("Comment", back_populates="driver")
    stars = relationship("Star", secondary="comments", viewonly=True, back_populates=None)

    car_type_id: Mapped[int] = mapped_column(ForeignKey("car_types.id"))
    car_type: Mapped["CarType"] = relationship("CarType", back_populates="drivers")


class DriverLocation(TimeBaseModel):
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), unique=True)
    driver: Mapped["Driver"] = relationship("Driver", back_populates="location")

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # MUHIM: start_time faqat mijoz oldiga yetganda boshlanadi
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Mijoz oldiga yetgan vaqt
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Kutish boshlanish vaqti
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Safar tugash vaqti

    toll: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)

    distance_km: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)
    waiting_fee: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)


class Comment(TimeBaseModel):
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    description: Mapped[str] = mapped_column(String(255), nullable=True)

    driver = relationship("Driver", back_populates="comments")
    user = relationship("User", back_populates="comments")
    stars = relationship("Star", back_populates="comment", cascade="all, delete-orphan")


class Star(TimeBaseModel):
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))
    value: Mapped[int] = mapped_column(Integer(), default=3)

    comment = relationship("Comment", back_populates="stars")
