from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.database.models.user import User
from bot.database.repositories import settings_repo
from bot.filters.chat_type import IsPrivateChat
from bot.keyboards.private_menu import main_menu_keyboard

router = Router(name="private_menu")
router.message.filter(IsPrivateChat())

DM_WELCOME_TEXT_KEY = "dm_welcome_text"

DEFAULT_WELCOME_TEXT = (
    "سلام رفیق به بنگ بنگ خوش اومدی 💊🔫\n"
    "از اینجا میتونی سلاح بخری، سگ بگیری، تیم بسازی و اکانتتو مدیریت کنی\n"
    "بریم سراغش 👇"
)


async def get_welcome_text() -> str:
    override = await settings_repo.get_override(DM_WELCOME_TEXT_KEY)
    return override or DEFAULT_WELCOME_TEXT


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    text = await get_welcome_text()
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User) -> None:
    await message.answer("منوی اصلی 👇", reply_markup=main_menu_keyboard())


@router.callback_query(lambda c: c.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, user: User) -> None:
    if callback.message.photo:
        # نمیشه پیام عکس‌دار رو edit_text کرد (مثلا وقتی از پروفایل با عکس برمی‌گردیم)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer("منوی اصلی 👇", reply_markup=main_menu_keyboard())
    else:
        await callback.message.edit_text("منوی اصلی 👇", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:add_to_group")
async def cb_add_to_group(callback: CallbackQuery) -> None:
    bot_info = await callback.bot.get_me()
    add_url = f"https://t.me/{bot_info.username}?startgroup=true"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ افزودن به گروه", url=add_url)],
            [InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")],
        ]
    )
    await callback.message.edit_text(
        "برای اضافه کردن ربات به گروهت، دکمه زیر رو بزن و گروه مقصد رو انتخاب کن\n"
        "یادت نره بعدش ادمینش کنی 🙏",
        reply_markup=keyboard,
    )
    await callback.answer()
