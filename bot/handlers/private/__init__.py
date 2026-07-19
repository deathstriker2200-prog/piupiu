from aiogram import Dispatcher

from bot.handlers.private.bank_handler import router as bank_router
from bot.handlers.private.building_handler import router as building_router
from bot.handlers.private.dog_handler import router as dog_router
from bot.handlers.private.equipment_handler import router as equipment_router
from bot.handlers.private.leaderboard_handler import router as leaderboard_router
from bot.handlers.private.menu_handler import router as menu_router
from bot.handlers.private.profile_handler import router as profile_router
from bot.handlers.private.quest_handler import router as quest_router
from bot.handlers.private.shop_handler import router as shop_router
from bot.handlers.private.team_handler import router as team_router


def register_private_handlers(dp: Dispatcher) -> None:
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(shop_router)
    dp.include_router(bank_router)
    dp.include_router(dog_router)
    dp.include_router(equipment_router)
    dp.include_router(building_router)
    dp.include_router(team_router)
    dp.include_router(quest_router)
    dp.include_router(leaderboard_router)
