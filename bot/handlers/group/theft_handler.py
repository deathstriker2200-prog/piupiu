from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database.models.user import User
from bot.filters.chat_type import IsGroupChat
from bot.keyboards.common import confirm_cancel_keyboard
from bot.services.theft_service import TheftError, attempt_theft
from bot.texts import theft_texts
from bot.utils.target_extraction import extract_target_user_id

router = Router(name="group_theft")
router.message.filter(IsGroupChat())


@router.message(Command("دزدی"))
async def handle_theft_command(message: Message, user: User) -> None:
    target_id = await extract_target_user_id(message)
    if target_id is None:
        await message.reply("از کی می‌خوای بدزدی؟ ریپلای بزن یا منشن کن 🥷")
        return

    if target_id == message.from_user.id:
        await message.reply("از خودت که نمیشه دزدید 😂")
        return

    target_name = (
        message.reply_to_message.from_user.full_name
        if message.reply_to_message and message.reply_to_message.from_user
        else "طرف"
    )

    await message.reply(
        f"{theft_texts.THEFT_WARNING}\nمطمئنی می‌خوای از {target_name} بدزدی؟",
        reply_markup=confirm_cancel_keyboard(
            confirm_callback=f"theft_confirm:{target_id}",
            cancel_callback="theft_cancel",
        ),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("theft_confirm:"))
async def handle_theft_confirm(callback: CallbackQuery, user: User) -> None:
    target_id = int(callback.data.split(":", 1)[1])
    thief_id = callback.from_user.id

    try:
        result = await attempt_theft(thief_id, target_id)
    except TheftError as e:
        await _handle_theft_error(callback, str(e))
        return

    if result["success"]:
        await callback.message.edit_text(
            theft_texts.theft_success(callback.from_user.full_name, "طرف", result["amount"])
        )
    else:
        await callback.message.edit_text(
            theft_texts.theft_fail(callback.from_user.full_name, result["jail_minutes"])
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "theft_cancel")
async def handle_theft_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_text("باشه بیخیال شدیم 😌")
    await callback.answer()


async def _handle_theft_error(callback: CallbackQuery, error: str) -> None:
    if error.startswith("jailed:"):
        minutes = int(error.split(":", 1)[1])
        await callback.message.edit_text(theft_texts.already_jailed(minutes))
    elif error == "thief_dead":
        await callback.message.edit_text("تو الان مردی نمیتونی دزدی کنی 💀")
    elif error == "target_no_money":
        await callback.message.edit_text(theft_texts.target_has_no_money())
    else:
        await callback.message.edit_text("یه مشکلی پیش اومد دوباره امتحان کن 😅")
    await callback.answer()
