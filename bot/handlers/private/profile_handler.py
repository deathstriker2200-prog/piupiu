from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.database.models.user import User
from bot.database.repositories import bank_repo, team_repo, weapon_repo
from bot.keyboards.common import back_keyboard
from bot.services.level_service import xp_required_for_level
from bot.services.stats_service import get_user_stats
from bot.utils.formatting import format_currency, hp_bar

router = Router(name="private_profile")


async def _build_profile_text(user: User) -> str:
    bank = await bank_repo.get_bank(user.user_id)
    bank_balance = bank["balance"] if bank else 0
    xp_needed = xp_required_for_level(user.level)
    stats = await get_user_stats(user.user_id)
    team = await team_repo.get_user_team(user.user_id)
    equipped = await weapon_repo.get_equipped_weapon(user.user_id)

    status_line = "☠️ مرده" if user.is_dead else ("🔒 زندانی" if user.jailed_until else "✅ زنده")
    team_line = f"{team.logo_emoji or '🏴'} {team.name}" if team else "بدون تیم"
    weapon_line = f"{equipped['emoji']} {equipped['name_fa']}" if equipped else "چیزی تجهیز نکرده"

    member_since = ""
    try:
        created_dt = datetime.fromisoformat(user.created_at)
        member_since = created_dt.strftime("%Y/%m/%d")
    except Exception:
        pass

    text = (
        f"╭━━━━━━━━━━━━━━━╮\n"
        f"   👤 {user.full_name or user.username or 'بازیکن'}\n"
        f"╰━━━━━━━━━━━━━━━╯\n\n"
        f"وضعیت: {status_line}\n"
        f"🏴 تیم: {team_line}\n"
        f"🔫 سلاح تجهیز شده: {weapon_line}\n\n"
        f"❤️ HP: {hp_bar(user.hp, user.max_hp)}  {user.hp}/{user.max_hp}\n"
        f"🌟 لول {user.level}  —  XP {user.xp}/{xp_needed}\n"
        f"🏆 رتبه: {stats['rank']} از {stats['total_players']} بازیکن\n\n"
        f"━━━━━━ 💰 دارایی ━━━━━━\n"
        f"💊 تریاک‌پوینت: {format_currency(user.tiriak_point)}\n"
        f"🏦 موجودی بانک: {format_currency(bank_balance)}\n\n"
        f"━━━━━━ ⚔️ آمار جنگی ━━━━━━\n"
        f"💀 کشته‌ها: {stats['kills']} (از {stats['attacks_made']} حمله - "
        f"{stats['win_rate']}% کشتار)\n"
        f"🩸 دمیج کل واردشده: {format_currency(stats['total_damage_dealt'])}\n"
        f"😵 دفعاتی که خوردی: {stats['times_attacked']} | مرگ: {stats['deaths']}\n"
        f"🥷 دزدی موفق: {stats['theft_success_count']} "
        f"({format_currency(stats['theft_success_amount'])} دزدیده) | "
        f"ناموفق: {stats['theft_fail_count']}\n\n"
        f"━━━━━━ 🏗 دارایی‌های دیگه ━━━━━━\n"
        f"🔫 سلاح‌های خریداری‌شده: {stats['weapons_owned']}\n"
        f"🐕 سگ‌ها: {stats['dogs_owned']}\n"
        f"🏗 مجموع لول ساختمان‌ها: {stats['buildings_total_level']}"
    )
    if member_since:
        text += f"\n\n🗓 عضو از {member_since}"
    return text


@router.message(Command("profile"))
async def cmd_profile(message: Message, user: User) -> None:
    text = await _build_profile_text(user)

    photo_bytes = None
    try:
        photos = await message.bot.get_user_profile_photos(user.user_id, limit=1)
        if photos.total_count > 0:
            file = await message.bot.get_file(photos.photos[0][-1].file_id)
            photo_bytes = await message.bot.download_file(file.file_path)
    except Exception:
        photo_bytes = None

    if photo_bytes:
        photo_file = BufferedInputFile(photo_bytes.read(), filename="profile.jpg")
        await message.answer_photo(photo_file, caption=text, reply_markup=back_keyboard("menu:main"))
    else:
        await message.answer(text, reply_markup=back_keyboard("menu:main"))


@router.callback_query(lambda c: c.data == "menu:profile")
async def cb_profile(callback: CallbackQuery, user: User) -> None:
    text = await _build_profile_text(user)

    photo_bytes = None
    try:
        photos = await callback.bot.get_user_profile_photos(user.user_id, limit=1)
        if photos.total_count > 0:
            file = await callback.bot.get_file(photos.photos[0][-1].file_id)
            photo_bytes = await callback.bot.download_file(file.file_path)
    except Exception:
        photo_bytes = None

    # اگه پیام قبلی متنی بوده و الان عکس داریم، باید پیام قدیمی رو پاک کنیم و پیام تازه با عکس بفرستیم
    # چون نمیشه یه پیام متنی رو به پیام عکس‌دار edit کرد
    if photo_bytes:
        photo_file = BufferedInputFile(photo_bytes.read(), filename="profile.jpg")
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer_photo(
            photo_file, caption=text, reply_markup=back_keyboard("menu:main")
        )
    else:
        await callback.message.edit_text(text, reply_markup=back_keyboard("menu:main"))

    await callback.answer()
