"""
حمله سگ تو گروه با پیام متنی: [اسم سگ] بگیرش (ریپلای روی پیام هدف)
مثلا: کامبیز بگیرش
"""

from aiogram import Router
from aiogram.types import Message

from bot.database.models.user import User
from bot.database.repositories import dog_repo
from bot.filters.chat_type import IsGroupChat
from bot.services.dog_service import DogError, attack_with_dog, find_user_dog_by_name
from bot.utils.formatting import format_seconds
from bot.utils.target_extraction import extract_target_user_id

router = Router(name="group_dog_attack")
router.message.filter(IsGroupChat())

TRIGGER_SUFFIX = "بگیرش"


@router.message(lambda m: m.text and m.text.strip().endswith(TRIGGER_SUFFIX))
async def handle_dog_attack_command(message: Message, user: User) -> None:
    raw = message.text.strip()
    dog_name = raw[: -len(TRIGGER_SUFFIX)].strip()
    if not dog_name:
        return

    dog = await find_user_dog_by_name(message.from_user.id, dog_name)
    if dog is None:
        # اگه اسمی که نوشته با هیچ سگی از این کاربر مچ نشه، این پیام برای ما نیست
        # (ممکنه فقط یه جمله عادی باشه که تصادفا به «بگیرش» ختم شده)
        return

    target_id = await extract_target_user_id(message)
    if target_id is None:
        await message.reply("رو کی می‌خوای سگتو بندازی؟ ریپلای بزن رو پیام طرف 🐶")
        return

    if target_id == message.from_user.id:
        await message.reply("سگتو رو خودت که نمی‌ندازی 😅")
        return

    try:
        result = await attack_with_dog(message.from_user.id, dog.id, target_id)
    except DogError as e:
        error = str(e)
        if error.startswith("cooldown:"):
            seconds_left = int(error.split(":", 1)[1])
            await message.reply(
                f"🕐 {dog.nickname} هنوز خسته‌ست، {format_seconds(seconds_left)} دیگه صبر کن"
            )
        elif error == "target_dead":
            await message.reply("طرف که همین الان مرده، بذار زنده بشه بعد بفرستش سراغش 💀")
        else:
            await message.reply("مشکلی پیش اومد، دوباره امتحان کن")
        return

    target_name = (
        message.reply_to_message.from_user.full_name
        if message.reply_to_message and message.reply_to_message.from_user
        else "حریف"
    )
    breed = await dog_repo.get_dog_breed(dog.dog_id)
    dog_emoji = breed.emoji if breed else "🐶"

    if result["target_died"]:
        await message.reply(
            f"{dog_emoji} {dog.nickname} پرید رو {target_name} و {result['damage']} دمیج زد!\n\n"
            f"☠️ {target_name} مُرد"
        )
    else:
        await message.reply(
            f"{dog_emoji} {dog.nickname} پرید رو {target_name} و {result['damage']} دمیج زد!\n\n"
            f"❤️ سلامتی باقی‌مانده {target_name}:\n"
            f"{result['target_remaining_hp']} / {result['target_max_hp']}"
        )
