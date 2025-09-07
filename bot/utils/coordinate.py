import math

from database import DriverLocation


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
        d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # km


async def get_nearest_driver(lat: float, lon: float):
    drivers_locations = await DriverLocation.all()

    nearest_driver = None
    min_distance = float("inf")

    for driver_loc in drivers_locations:
        dist = haversine(lat, lon, driver_loc.latitude, driver_loc.longitude)
        if dist < min_distance:
            min_distance = dist
            nearest_driver = driver_loc.driver_id

    return nearest_driver, min_distance
