import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.config.settings import settings
from bot.filters.is_admin import IsAdmin
from bot.keyboards.common import confirm_cancel_keyboard
from bot.services.backup_service import create_backup_copy, restore_from_file

router = Router(name="admin_backup")
router.message.filter(IsAdmin())


class BackupStates(StatesGroup):
    waiting_restore_file = State()


@router.message(Command("backup"))
async def cmd_backup(message: Message) -> None:
    try:
        backup_path = create_backup_copy()
    except FileNotFoundError:
        await message.reply("فایل دیتابیس هنوز ساخته نشده یه کاری تو ربات انجام بده اول")
        return

    await message.reply_document(
        FSInputFile(backup_path),
        caption="📦 این بک‌آپ دیتابیس فعلیه، جایی امن نگهش دار",
    )


@router.message(Command("restore"))
async def cmd_restore_prompt(message: Message, state: FSMContext) -> None:
    await message.reply(
        "⚠️ توجه\n"
        "فایل .db که الان بفرستی جای دیتابیس فعلی رو کاملا می‌گیره "
        "و همه چیز فعلی از بین میره\n"
        "یه فایل .db بفرست تا ادامه بدیم"
    )
    await state.set_state(BackupStates.waiting_restore_file)


@router.message(BackupStates.waiting_restore_file, lambda m: m.document is not None)
async def handle_restore_file(message: Message, state: FSMContext) -> None:
    document = message.document
    if not document.file_name or not document.file_name.endswith(".db"):
        await message.reply("این فایل .db نیست دوباره امتحان کن یا لغو کن")
        return

    temp_path = f"/tmp/restore_upload_{message.from_user.id}.db"
    file = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file.file_path, destination=temp_path)

    await state.update_data(temp_path=temp_path)
    await message.reply(
        f"فایل {document.file_name} گرفتم مطمئنی می‌خوای جایگزین دیتابیس فعلی بشه؟",
        reply_markup=confirm_cancel_keyboard(
            confirm_callback="restore_confirm", cancel_callback="restore_cancel"
        ),
    )


@router.message(BackupStates.waiting_restore_file)
async def handle_restore_no_file(message: Message) -> None:
    await message.reply("باید یه فایل .db بفرستی نه متن")


@router.callback_query(lambda c: c.data == "restore_confirm")
async def cb_restore_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    temp_path = data.get("temp_path")

    if not temp_path or not os.path.exists(temp_path):
        await callback.message.edit_text("فایل آپلودی دیگه پیدا نشد از اول امتحان کن")
        await state.clear()
        await callback.answer()
        return

    safety_backup = restore_from_file(temp_path)
    os.remove(temp_path)
    await state.clear()

    text = "✅ دیتابیس با فایل جدید جایگزین شد از الان همه چی از رو اون فایله"
    if safety_backup:
        text += f"\n\nیه بک‌آپ از وضعیت قبلی هم گرفتم اگه لازم شد از سرور قابل بازیابیه"
    await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(lambda c: c.data == "restore_cancel")
async def cb_restore_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    temp_path = data.get("temp_path")
    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)
    await state.clear()
    await callback.message.edit_text("ریستور لغو شد دیتابیس فعلی دست‌نخورده موند")
    await callback.answer()
