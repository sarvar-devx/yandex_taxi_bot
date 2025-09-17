from aiogram import Router

from bot.handlers.driver.base import driver_router
from bot.handlers.driver.driver_info import driver_info_router

driver_routers = Router()
driver_routers.include_routers(driver_router, driver_info_router)