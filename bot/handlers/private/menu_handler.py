from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.database.models.user import User
from bot.filters.chat_type import IsPrivateChat
from bot.keyboards.private_menu import main_menu_keyboard

router = Router(name="private_menu")
router.message.filter(IsPrivateChat())

WELCOME_TEXT = (
    "سلام رفیق به تریاکی پیو پیو خوش اومدی 💊🔫\n"
    "از اینجا میتونی سلاح بخری، سگ بگیری، تیم بسازی و اکانتتو مدیریت کنی\n"
    "بریم سراغش 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("منو"))
async def cmd_menu(message: Message, user: User) -> None:
    await message.answer("منوی اصلی 👇", reply_markup=main_menu_keyboard())


@router.callback_query(lambda c: c.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, user: User) -> None:
    await callback.message.edit_text("منوی اصلی 👇", reply_markup=main_menu_keyboard())
    await callback.answer()
