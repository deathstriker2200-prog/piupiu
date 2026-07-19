from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.database.models.user import User
from bot.database.repositories import team_repo
from bot.keyboards.common import back_keyboard
from bot.keyboards.team_kb import join_request_keyboard, team_menu_keyboard
from bot.services.team_service import TeamError, create_team, request_join, respond_to_request
from bot.texts.common_texts import not_enough_money
from bot.texts.team_texts import (
    already_in_team,
    join_accepted,
    join_rejected,
    join_request_received,
    join_request_sent,
    left_team,
    team_created,
)

router = Router(name="private_team")


class TeamStates(StatesGroup):
    waiting_team_name = State()
    waiting_join_team_name = State()


@router.callback_query(lambda c: c.data == "menu:team")
async def cb_team_menu(callback: CallbackQuery, user: User) -> None:
    team = await team_repo.get_user_team(user.user_id)
    if team:
        text = f"🏴 تیم تو: {team.name}\n{team.description or ''}"
    else:
        text = "هنوز عضو هیچ تیمی نیستی"
    await callback.message.edit_text(text, reply_markup=team_menu_keyboard(team is not None))
    await callback.answer()


@router.callback_query(lambda c: c.data == "team:create")
async def cb_team_create_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "اسم تیمت چی باشه؟ بفرست", reply_markup=back_keyboard("menu:team")
    )
    await state.set_state(TeamStates.waiting_team_name)
    await callback.answer()


@router.message(TeamStates.waiting_team_name)
async def handle_team_name(message: Message, user: User, state: FSMContext) -> None:
    name = message.text.strip() if message.text else ""
    if not name:
        await message.reply("اسم معتبر بفرست")
        return
    try:
        await create_team(user.user_id, name, "🏴", "")
        await message.reply(team_created(name), reply_markup=back_keyboard("menu:main"))
    except TeamError as e:
        if str(e) == "already_in_team":
            await message.reply(already_in_team())
        elif str(e) == "name_taken":
            await message.reply("این اسم قبلا گرفته شده یه اسم دیگه بفرست")
            return
        elif str(e) == "not_enough_money":
            await message.reply(not_enough_money())
    await state.clear()


@router.callback_query(lambda c: c.data == "team:search")
async def cb_team_search_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "اسم دقیق تیمی که می‌خوای بهش بپیوندی رو بفرست", reply_markup=back_keyboard("menu:team")
    )
    await state.set_state(TeamStates.waiting_join_team_name)
    await callback.answer()


@router.message(TeamStates.waiting_join_team_name)
async def handle_join_team_name(message: Message, user: User, state: FSMContext) -> None:
    name = message.text.strip() if message.text else ""
    team = await team_repo.get_team_by_name(name)
    if team is None:
        await message.reply("همچین تیمی پیدا نشد دوباره امتحان کن")
        return

    try:
        request_id = await request_join(user.user_id, team.team_id)
    except TeamError as e:
        if str(e) == "already_in_team":
            await message.reply(already_in_team())
        elif str(e) == "team_full":
            await message.reply("این تیم پره جای دیگه رو امتحان کن")
        else:
            await message.reply("مشکلی پیش اومد")
        await state.clear()
        return

    await message.reply(join_request_sent(team.name), reply_markup=back_keyboard("menu:main"))
    await state.clear()

    # اطلاع به لیدر تیم با دکمه‌های قبول ✅ / رد ❌
    try:
        await message.bot.send_message(
            team.owner_id,
            join_request_received(message.from_user.full_name, team.name),
            reply_markup=join_request_keyboard(request_id),
        )
    except Exception:
        pass


@router.callback_query(lambda c: c.data and c.data.startswith("team_req_accept:"))
async def cb_team_request_accept(callback: CallbackQuery, user: User) -> None:
    request_id = int(callback.data.split(":", 1)[1])
    try:
        result = await respond_to_request(request_id, accept=True)
    except TeamError:
        await callback.answer("این درخواست دیگه معتبر نیست", show_alert=True)
        return
    await callback.message.edit_text(f"✅ عضو جدید قبول شد به تیم {result['team_name']}")
    await callback.answer()
    try:
        await callback.bot.send_message(result["user_id"], join_accepted(result["team_name"]))
    except Exception:
        pass


@router.callback_query(lambda c: c.data and c.data.startswith("team_req_reject:"))
async def cb_team_request_reject(callback: CallbackQuery, user: User) -> None:
    request_id = int(callback.data.split(":", 1)[1])
    try:
        result = await respond_to_request(request_id, accept=False)
    except TeamError:
        await callback.answer("این درخواست دیگه معتبر نیست", show_alert=True)
        return
    await callback.message.edit_text(f"❌ درخواست رد شد")
    await callback.answer()
    try:
        await callback.bot.send_message(result["user_id"], join_rejected(result["team_name"]))
    except Exception:
        pass


@router.callback_query(lambda c: c.data == "team:leave_confirm")
async def cb_team_leave(callback: CallbackQuery, user: User) -> None:
    from bot.services.team_service import leave_team

    team = await team_repo.get_user_team(user.user_id)
    if team is None:
        await callback.answer("تو الان تو تیمی نیستی", show_alert=True)
        return
    try:
        await leave_team(user.user_id)
    except TeamError as e:
        if str(e) == "owner_cannot_leave":
            await callback.answer("لیدر تیم نمیتونه خارج بشه اول باید تیم رو منتقل کنی", show_alert=True)
        return
    await callback.message.edit_text(left_team(team.name), reply_markup=back_keyboard("menu:main"))
    await callback.answer()
