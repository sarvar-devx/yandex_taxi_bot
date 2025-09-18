import math

from database import DriverLocation, Driver


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
        d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # km


async def get_nearest_driver(lat: float, lon: float, car_type_id: int):
    drivers = await Driver.filter(Driver.car_type_id == car_type_id)
    drivers_locations = await DriverLocation.filter(DriverLocation.driver_id == drivers[0].id)

    # drivers_ids = [d.id for d in drivers]
    # drivers_locations = await DriverLocation.filter(driver_in=drivers_ids)

    nearest_driver = None
    min_distance = float("inf")

    for driver_loc in drivers_locations:
        dist = haversine(lat, lon, driver_loc.latitude, driver_loc.longitude)
        if dist < min_distance:
            min_distance = dist
            nearest_driver = driver_loc.driver_id

    return nearest_driver, min_distance


async def calculate_arrival_time(distance: float) -> str:
    """
    Masofaga qarab taxminiy kelish vaqtini hisoblaydi.
    :param distance: km
    :return: vaqt string ko‘rinishda ("7 daqiqa", "1 soat 15 daqiqa")
    """
    average_speed = 50  # km/h
    time_minutes = (distance / average_speed) * 60

    minutes = int(round(time_minutes))
    if minutes < 60:
        return f"{minutes} daqiqa"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours} soat {mins} daqiqa"
