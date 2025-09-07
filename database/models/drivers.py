from enum import Enum

from sqlalchemy import Enum as SqlAlchemyEnum, Integer
from sqlalchemy import String, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel


class Driver(TimeBaseModel):
    class CarType(Enum):
        START = "start"
        COMFORT = "comfort"
        BUSINESS = "business"
        PREMIER = "premier"

    image: Mapped[str] = mapped_column(String(255))
    car_brand: Mapped[str] = mapped_column(String(255))
    car_number: Mapped[str] = mapped_column(String(15))
    license_term: Mapped[str] = mapped_column(String(255))
    car_type: Mapped[SqlAlchemyEnum] = mapped_column(SqlAlchemyEnum(CarType), default=CarType.START)
    has_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    has_client: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="driver_profile")
    location: Mapped["DriverLocation"] = relationship("DriverLocation", back_populates="driver", uselist=False)
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="driver")
    comments = relationship("Comment", back_populates="driver")
    stars = relationship("Star", secondary="comments", viewonly=True, back_populates=None)


class DriverLocation(TimeBaseModel):
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), unique=True)
    driver: Mapped["Driver"] = relationship("Driver", back_populates="location")

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


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
