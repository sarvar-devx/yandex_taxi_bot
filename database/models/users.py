from enum import Enum

from sqlalchemy import String, Boolean, ForeignKey, Float, Text
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


# Userni borish manzili
class Address(TimeBaseModel):
    __tablename__ = "addresses"

    class AddressType(Enum):
        HOME = "home"                   # Uy manzili
        WORK = "work"                   # Ish joyi
        PICKUP = "pickup"               # Olib ketish nuqtasi
        DESTINATION = "destination"     # Borish nuqtasi
        FAVORITE = "favorite"           # Sevimli joy

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="addresses")

    # Koordinatalar
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Manzil ma'lumotlari
    address_type: Mapped[AddressType] = mapped_column(default=AddressType.PICKUP)
    title: Mapped[str] = mapped_column(String(100), nullable=True)  # "Uy", "Ish", "Do'kon"
    full_address: Mapped[str] = mapped_column(Text, nullable=True)  # To'liq manzil

    # Qo'shimcha ma'lumotlar
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_count: Mapped[int] = mapped_column(default=0)  # Necha marta ishlatilgan

    # Relationships
    pickup_orders: Mapped[list["Order"]] = relationship("Order",
                                                        foreign_keys="[Order.pickup_address_id]",
                                                        back_populates="pickup_address")
    destination_orders: Mapped[list["Order"]] = relationship("Order",
                                                        foreign_keys="[Order.destination_address_id]",
                                                        back_populates="destination_address")
