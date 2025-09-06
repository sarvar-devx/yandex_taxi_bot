import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import DriverLocation


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
        d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # km


async def get_nearest_driver(session: AsyncSession, lat: float, lon: float):
    result = await session.execute(select(DriverLocation))
    drivers = result.scalars().all()

    nearest_driver = None
    min_distance = float("inf")

    for driver in drivers:
        dist = haversine(lat, lon, driver.latitude, driver.longitude)
        if dist < min_distance:
            min_distance = dist
            nearest_driver = driver

    return nearest_driver, min_distance
