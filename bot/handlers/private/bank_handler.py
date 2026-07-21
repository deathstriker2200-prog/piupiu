from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.database.models.user import User
from bot.database.repositories import bank_repo
from bot.filters.chat_type import IsPrivateChat
from bot.keyboards.common import back_keyboard
from bot.services.bank_service import BankError, deposit, upgrade_bank, withdraw
from bot.texts.common_texts import (
    deposit_fail_capacity,
    deposit_success,
    not_enough_money,
    withdraw_fail_balance,
    withdraw_success,
)
from bot.utils.formatting import format_currency

router = Router(name="private_bank")
router.message.filter(IsPrivateChat())


class BankStates(StatesGroup):
    waiting_deposit_amount = State()
    waiting_withdraw_amount = State()


def bank_menu_keyboard():
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬆️ واریز", callback_data="bank:deposit"),
                InlineKeyboardButton(text="⬇️ برداشت", callback_data="bank:withdraw"),
            ],
            [InlineKeyboardButton(text="✅ ارتقای ظرفیت", callback_data="bank:upgrade")],
            [InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")],
        ]
    )


@router.callback_query(lambda c: c.data == "menu:bank")
async def cb_bank_menu(callback: CallbackQuery, user: User) -> None:
    bank = await bank_repo.get_bank(user.user_id)
    balance = bank["balance"] if bank else 0
    capacity = bank["capacity"] if bank else 0
    text = (
        f"🏦 بانک شخصی تو\n\n"
        f"موجودی: {format_currency(balance)}\n"
        f"ظرفیت: {format_currency(capacity)}"
    )
    await callback.message.edit_text(text, reply_markup=bank_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "bank:deposit")
async def cb_bank_deposit_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "چقدر می‌خوای واریز کنی؟ عدد بفرست", reply_markup=back_keyboard("menu:bank")
    )
    await state.set_state(BankStates.waiting_deposit_amount)
    await callback.answer()


@router.message(BankStates.waiting_deposit_amount)
async def handle_deposit_amount(message: Message, user: User, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.reply("فقط عدد بفرست 🔢")
        return
    amount = int(message.text)
    try:
        await deposit(user.user_id, amount)
        await message.reply(deposit_success(amount), reply_markup=back_keyboard("menu:bank"))
    except BankError as e:
        if str(e) == "not_enough_money":
            await message.reply(not_enough_money())
        elif str(e) == "capacity_full":
            await message.reply(deposit_fail_capacity())
        else:
            await message.reply("عدد نامعتبره")
    await state.clear()


@router.callback_query(lambda c: c.data == "bank:withdraw")
async def cb_bank_withdraw_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "چقدر می‌خوای برداشت کنی؟ عدد بفرست", reply_markup=back_keyboard("menu:bank")
    )
    await state.set_state(BankStates.waiting_withdraw_amount)
    await callback.answer()


@router.message(BankStates.waiting_withdraw_amount)
async def handle_withdraw_amount(message: Message, user: User, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.reply("فقط عدد بفرست 🔢")
        return
    amount = int(message.text)
    try:
        await withdraw(user.user_id, amount)
        await message.reply(withdraw_success(amount), reply_markup=back_keyboard("menu:bank"))
    except BankError as e:
        if str(e) == "not_enough_balance":
            await message.reply(withdraw_fail_balance())
        else:
            await message.reply("عدد نامعتبره")
    await state.clear()


@router.callback_query(lambda c: c.data == "bank:upgrade")
async def cb_bank_upgrade(callback: CallbackQuery, user: User) -> None:
    try:
        new_capacity = await upgrade_bank(user.user_id)
    except BankError:
        await callback.answer(not_enough_money(), show_alert=True)
        return
    await callback.answer(f"✅ ظرفیت بانک رفت رو {format_currency(new_capacity)}", show_alert=True)
    await cb_bank_menu(callback, user)
