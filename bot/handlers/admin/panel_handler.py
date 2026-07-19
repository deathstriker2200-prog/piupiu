from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.database.db import get_conn
from bot.database.repositories import user_repo, weapon_repo
from bot.filters.is_admin import IsAdmin
from bot.keyboards.admin_kb import admin_confirm_action_keyboard, admin_main_keyboard
from bot.keyboards.common import back_keyboard
from bot.services.stats_service import get_global_stats
from bot.utils.formatting import format_currency

router = Router(name="admin_panel")
router.message.filter(IsAdmin())


class AdminStates(StatesGroup):
    waiting_broadcast_text = State()
    waiting_grant_target = State()
    waiting_grant_amount = State()
    waiting_ban_target = State()


@router.message(Command("ادمین"))
async def cmd_admin(message: Message) -> None:
    await message.answer("⚙️ پنل ادمین", reply_markup=admin_main_keyboard())


@router.callback_query(lambda c: c.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery) -> None:
    stats = await get_global_stats()

    top_weapon_name = "-"
    if stats["top_weapon"]:
        w = await weapon_repo.get_weapon(stats["top_weapon"])
        if w:
            top_weapon_name = f"{w.emoji} {w.name_fa}"

    text = (
        "📊 آمار کلی بازی\n\n"
        f"👥 کل کاربران: {stats['total_users']}\n"
        f"🚫 بن‌شده: {stats['banned_users']}\n"
        f"💀 الان مرده: {stats['dead_now']}\n"
        f"🔒 الان زندانی: {stats['jailed_now']}\n"
        f"🌟 میانگین لول: {stats['avg_level']}\n\n"
        f"🏴 تعداد تیم‌ها: {stats['total_teams']}\n"
        f"🐕 مجموع سگ‌ها: {stats['total_dogs']}\n"
        f"🔫 پرفروش‌ترین سلاح: {top_weapon_name}\n\n"
        f"⚔️ مجموع حمله‌ها: {stats['total_attacks']}\n"
        f"💀 مجموع کشته‌ها: {stats['total_kills']}\n"
        f"🥷 دزدی موفق: {stats['total_theft_success']} | ناموفق: {stats['total_theft_fail']}\n\n"
        f"💊 مجموع تریاک‌پوینت در گردش: {format_currency(stats['total_tiriak_in_economy'])}\n"
        f"🏦 مجموع موجودی بانک‌ها: {format_currency(stats['total_bank_balance'])}"
    )
    await callback.message.edit_text(text, reply_markup=back_keyboard("admin:main"))
    await callback.answer()



@router.callback_query(lambda c: c.data == "admin:main")
async def cb_admin_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text("⚙️ پنل ادمین", reply_markup=admin_main_keyboard())
    await callback.answer()


# --- ارسال همگانی ---


@router.callback_query(lambda c: c.data == "admin:broadcast")
async def cb_admin_broadcast_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "متن پیام همگانی رو بفرست", reply_markup=back_keyboard("admin:main")
    )
    await state.set_state(AdminStates.waiting_broadcast_text)
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_text)
async def handle_broadcast_text(message: Message, state: FSMContext) -> None:
    text = message.text
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT user_id FROM users WHERE is_banned = 0")
        rows = await cursor.fetchall()

    sent = 0
    failed = 0
    for row in rows:
        try:
            await message.bot.send_message(row["user_id"], text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"📢 ارسال شد به {sent} نفر (ناموفق: {failed})")
    await state.clear()


# --- دادن پول/XP/الماس ---


@router.callback_query(lambda c: c.data == "admin:grant")
async def cb_admin_grant_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "آیدی عددی کاربر رو بفرست", reply_markup=back_keyboard("admin:main")
    )
    await state.set_state(AdminStates.waiting_grant_target)
    await callback.answer()


@router.message(AdminStates.waiting_grant_target)
async def handle_grant_target(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.reply("فقط آیدی عددی بفرست")
        return
    await state.update_data(target_id=int(message.text))
    await message.reply(
        "چی می‌خوای بدی؟ به این شکل بفرست:\ntiriak 1000\nxp 500\ndiamond 10"
    )
    await state.set_state(AdminStates.waiting_grant_amount)


@router.message(AdminStates.waiting_grant_amount)
async def handle_grant_amount(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    target_id = data.get("target_id")

    parts = (message.text or "").split()
    if len(parts) != 2 or not parts[1].lstrip("-").isdigit():
        await message.reply("فرمت اشتباهه مثال: tiriak 1000")
        return

    kind, amount_str = parts
    amount = int(amount_str)

    if kind == "tiriak":
        await user_repo.adjust_tiriak(target_id, amount)
    elif kind == "xp":
        from bot.services.level_service import add_xp_and_check_levelup

        await add_xp_and_check_levelup(target_id, amount)
    elif kind == "diamond":
        await user_repo.adjust_diamond(target_id, amount)
    else:
        await message.reply("نوع نامعتبره - tiriak یا xp یا diamond")
        return

    await message.reply(f"✅ انجام شد {amount} {kind} به {target_id} داده شد")
    await state.clear()


# --- بن/آن‌بن ---


@router.callback_query(lambda c: c.data == "admin:ban")
async def cb_admin_ban_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "آیدی عددی کاربر رو بفرست، بعدش می‌پرسم بن کنم یا آن‌بن",
        reply_markup=back_keyboard("admin:main"),
    )
    await state.set_state(AdminStates.waiting_ban_target)
    await callback.answer()


@router.message(AdminStates.waiting_ban_target)
async def handle_ban_target(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.reply("فقط آیدی عددی بفرست")
        return
    target_id = int(message.text)
    await message.reply(
        f"کاربر {target_id} رو بن کنم؟",
        reply_markup=admin_confirm_action_keyboard(f"ban:{target_id}"),
    )
    await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith("admin_confirm:ban:"))
async def cb_admin_confirm_ban(callback: CallbackQuery) -> None:
    target_id = int(callback.data.split(":")[-1])
    await user_repo.set_banned(target_id, True)
    await callback.message.edit_text(f"🚫 کاربر {target_id} بن شد")
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("admin_cancel:ban:"))
async def cb_admin_cancel_ban(callback: CallbackQuery) -> None:
    await callback.message.edit_text("لغو شد")
    await callback.answer()
