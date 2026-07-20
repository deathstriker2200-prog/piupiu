from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.models.user import User
from bot.filters.chat_type import IsGroupChat
from bot.services.combat_service import AttackResult, CombatError, resolve_attack
from bot.texts import battle_texts
from bot.utils.target_extraction import extract_target_user_id

router = Router(name="group_attack")
router.message.filter(IsGroupChat())


ATTACK_TRIGGERS = {"بنگ", "🔫"}


@router.message(Command("bang"))
@router.message(lambda m: m.text and m.text.strip().split()[0].lstrip("/") in ATTACK_TRIGGERS)
async def handle_attack(message: Message, user: User) -> None:
    target_id = await extract_target_user_id(message)
    if target_id is None:
        await message.reply("رو کی می‌خوای شلیک کنی؟ ریپلای بزن یا منشن کن 🔫")
        return

    if target_id == message.from_user.id:
        await message.reply("به خودت شلیک نکن روانی 😂")
        return

    target_user_obj = (
        message.reply_to_message.from_user
        if message.reply_to_message and message.reply_to_message.from_user
        else None
    )
    if target_user_obj and target_user_obj.is_bot:
        if target_user_obj.id == message.bot.id:
            await message.reply("رو من که نمیشه شلیک کرد داداش من رفرمو میدم نه HP 😎")
        else:
            await message.reply("رو ربات‌ها نمیشه شلیک کرد یه آدم واقعی رو نشونه بگیر 🎯")
        return

    try:
        result: AttackResult = await resolve_attack(message.from_user.id, target_id)
    except CombatError as e:
        await _handle_combat_error(message, str(e))
        return

    target_name = (
        message.reply_to_message.from_user.full_name
        if message.reply_to_message and message.reply_to_message.from_user
        else "حریف"
    )

    text = battle_texts.attack_result_v2(
        flavor_text=result.flavor_text,
        outcome=result.outcome,
        damage=result.damage,
        remaining_hp=result.target_remaining_hp,
        stolen=result.tiriak_stolen,
        combo_count=result.combo_count,
        combo_bonus_applied=result.combo_damage_bonus_applied,
    )
    await message.reply(text)

    if result.target_died:
        await message.answer(battle_texts.target_died(target_name))

        # چک اینکه آیا بانک قربانی خالی بوده و پول از دست رفته یا نه رو داخل combat_service مدیریت کردیم
        from bot.database.repositories import bank_repo

        bank = await bank_repo.get_bank(target_id)
        if bank and bank["balance"] > 0:
            await message.answer(battle_texts.death_bank_safe())

    # ردیابی کوئست حمله
    from bot.services.quest_service import track_progress

    completed = await track_progress(message.from_user.id, "attacks")
    if result.target_died:
        completed += await track_progress(message.from_user.id, "kills")

    from bot.texts.common_texts import quest_completed

    for q in completed:
        await message.answer(
            quest_completed(q["title"], q["reward_xp"], q["reward_tiriak"], q["reward_diamond"])
        )

    # ردیابی دستاورد و نشان
    from bot.services.achievement_service import bump_progress
    from bot.services.badge_service import evaluate_badges
    from bot.texts.achievement_texts import achievement_unlocked, badge_earned

    unlocked_achievements = await bump_progress(message.from_user.id, "attacks_made")
    if result.target_died:
        unlocked_achievements += await bump_progress(message.from_user.id, "kills")
    if result.outcome == "critical" or result.outcome == "headshot":
        unlocked_achievements += await bump_progress(message.from_user.id, "criticals_landed")
    if result.outcome == "lucky_hit":
        unlocked_achievements += await bump_progress(message.from_user.id, "lucky_hits")
    if result.outcome == "perfect_block":
        unlocked_achievements += await bump_progress(target_id, "perfect_blocks")
    if result.combo_count:
        unlocked_achievements += await bump_progress(
            message.from_user.id, "max_combo_reached", result.combo_count
        )

    for ach in unlocked_achievements:
        await message.answer(achievement_unlocked(ach["icon"], ach["title"], ach["description"]))

    new_badges = await evaluate_badges(message.from_user.id)
    for badge_id in new_badges:
        await message.answer(await badge_earned(badge_id))


async def _handle_combat_error(message: Message, error: str) -> None:
    if error == "attacker_dead":
        await message.reply(battle_texts.attacker_is_dead())
    elif error == "attacker_jailed":
        await message.reply(battle_texts.attacker_is_jailed(0))
    elif error == "target_dead":
        await message.reply(battle_texts.target_is_dead_already("حریف"))
    elif error == "no_weapon":
        await message.reply(battle_texts.no_weapon_equipped())
    elif error.startswith("cooldown:"):
        seconds_left = int(error.split(":", 1)[1])
        await message.reply(battle_texts.cooldown_active(seconds_left))
    elif error.startswith("out_of_ammo:"):
        weapon_name = error.split(":", 1)[1]
        await message.reply(battle_texts.out_of_ammo(weapon_name))
    elif error.startswith("not_enough_energy:"):
        _, current, needed = error.split(":")
        await message.reply(battle_texts.not_enough_energy(int(current), int(needed)))
    elif "پیدا نشد" in error:
        await message.reply("این هدف تو بازی ثبت نشده، باید حداقل یه بار با ربات تو پیوی /start زده باشه 🤔")
    else:
        await message.reply("این حمله انجام نشد یه چیزی جلوشو گرفت، دوباره امتحان کن 😅")
