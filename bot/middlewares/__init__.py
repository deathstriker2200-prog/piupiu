from aiogram import Dispatcher

from bot.middlewares.user_middleware import UserRegistrationMiddleware


def register_all_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(UserRegistrationMiddleware())
    dp.callback_query.middleware(UserRegistrationMiddleware())
