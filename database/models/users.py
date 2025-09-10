from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import TimeBaseModel


class User(TimeBaseModel):
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), unique=True, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    driver_profile: Mapped["Driver"] = relationship("Driver", back_populates="user", uselist=False, lazy="selectin")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    comments = relationship("Comment", back_populates="user")

    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="user")
    # Kop manzillar bolishi mummkun

# Manzil
class Address(TimeBaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="Addresses")

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
