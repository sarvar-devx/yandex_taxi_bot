from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TimeBaseModel

class User(TimeBaseModel):
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), unique=True, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    driver_profile: Mapped["Driver"] = relationship("Driver", back_populates="user", uselist=False)
    orders: Mapped[list["OrderTaxi"]] = relationship("OrderTaxi", back_populates="user")
