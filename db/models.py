from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import TimeBaseModel


class User(TimeBaseModel):
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12))


class Driver(User):
    image: Mapped[str] = mapped_column(String(255))
    car_category: Mapped[str] = mapped_column(String(255))
    car_number: Mapped[str] = mapped_column(String(8))
    license_term: Mapped[str] = mapped_column(String(255))
