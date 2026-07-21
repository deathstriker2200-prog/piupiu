"""
داده‌های اولیه نسخه ۲: دستاوردها، نشان‌ها، متن‌های حمله متنوع، Skill Tree ساختمان‌ها، مهارت سگ
"""

from bot.database.db import get_conn

# ================================================================
# دستاوردها (Achievement) - بیش از ۱۰۰ تا، دسته‌بندی شده
# هر دسته یک goal_type داره که با کد داخلی چک میشه (نه اسم رایج بازی‌های دیگه)
# ================================================================

ACHIEVEMENTS: list[tuple] = []


def _add_tier_set(prefix: str, icon: str, title_base: str, desc_base: str, goal_type: str,
                   thresholds: list[int], reward_scale: tuple[int, int, int]):
    """یک رده از دستاورد با چند سطح (برنز تا الماسی) می‌سازه"""
    tiers = ["bronze", "silver", "gold", "platinum"]
    for i, threshold in enumerate(thresholds):
        tier = tiers[min(i, len(tiers) - 1)]
        mult = i + 1
        ACHIEVEMENTS.append((
            f"{prefix}_{i+1}",
            icon,
            f"{title_base} {['یک', 'دو', 'سه', 'چهار'][min(i,3)]}",
            f"{desc_base} {threshold}",
            goal_type,
            threshold,
            reward_scale[0] * mult,
            reward_scale[1] * mult,
            reward_scale[2] * mult,
            tier,
        ))


_add_tier_set("combat_attacks", "⚔️", "رزمنده خیابونی", "به این تعداد حمله بزن:", "attacks_made",
              [10, 50, 200, 1000], (20, 50, 0))
_add_tier_set("combat_kills", "💀", "شکارچی", "این تعداد بازیکن رو بکش:", "kills",
              [5, 25, 100, 500], (30, 80, 1))
_add_tier_set("combat_damage", "🩸", "طوفان دمیج", "این مقدار دمیج کل وارد کن:", "total_damage",
              [500, 5000, 25000, 100000], (25, 60, 0))
_add_tier_set("survive_deaths", "🧟", "زنده‌مونده", "این تعداد بار بمیر و respawn شو:", "deaths_survived",
              [1, 10, 50, 200], (10, 20, 0))
_add_tier_set("theft_success", "🥷", "دله‌دزد", "این تعداد دزدی موفق انجام بده:", "theft_success",
              [1, 10, 50, 200], (20, 40, 0))
_add_tier_set("wealth_tiriak", "💊", "میلیاردر تریاکی", "این مقدار تریاک‌پوینت جمع کن:", "tiriak_earned",
              [1000, 10000, 100000, 1000000], (0, 100, 1))
_add_tier_set("wealth_bank", "🏦", "بانکدار محتاط", "این مقدار تو بانک پس‌انداز کن:", "bank_saved",
              [1000, 10000, 100000, 500000], (0, 50, 0))
_add_tier_set("level_reach", "🌟", "صعودگر", "به این لول برس:", "level_reached",
              [5, 15, 30, 50], (0, 200, 2))
_add_tier_set("dog_collector", "🐕", "سگ‌باز حرفه‌ای", "این تعداد سگ داشته باش:", "dogs_owned",
              [1, 3, 5, 8], (10, 100, 0))
_add_tier_set("dog_feed", "🍖", "غذاده باوفا", "این تعداد بار به سگ غذا بده:", "dog_feeds",
              [5, 25, 100, 500], (10, 30, 0))
_add_tier_set("weapon_collector", "🔫", "اسلحه‌چی", "این تعداد سلاح مختلف بخر:", "weapons_owned",
              [3, 8, 15, 24], (0, 150, 1))
_add_tier_set("building_upgrade", "🏗", "سازنده امپراطوری", "مجموع لول ساختمان‌هات به این برسه:", "buildings_total_level",
              [5, 20, 50, 100], (0, 200, 2))
_add_tier_set("team_join", "🏴", "هم‌تیمی خوب", "این تعداد روز عضو یه تیم باش:", "days_in_team",
              [1, 7, 30, 90], (20, 0, 0))
_add_tier_set("quest_complete", "📜", "کوئست‌باز", "این تعداد کوئست تموم کن:", "quests_completed",
              [5, 25, 100, 300], (30, 50, 0))
_add_tier_set("daily_streak", "🔥", "منظم همیشگی", "این تعداد روز پشت سر هم بیا تو ربات:", "login_streak",
              [3, 7, 30, 100], (0, 80, 2))
_add_tier_set("gift_sent", "🎁", "دست‌ودل‌باز", "این تعداد هدیه برای بقیه بفرست:", "gifts_sent",
              [1, 10, 50, 200], (0, 30, 0))
_add_tier_set("market_sales", "🛒", "بازاری کارکشته", "این تعداد آیتم تو بازار بفروش:", "market_sales",
              [1, 10, 50, 150], (0, 60, 0))
_add_tier_set("craft_items", "🛠", "صنعتگر زیرزمینی", "این تعداد آیتم بساز:", "items_crafted",
              [1, 10, 50, 200], (15, 30, 0))
_add_tier_set("boss_participate", "👹", "شکارچی غول", "این تعداد بار تو Boss Event شرکت کن:", "boss_participations",
              [1, 5, 20, 50], (0, 100, 1))
_add_tier_set("combo_reach", "⚡", "استاد کمبو", "به این عدد کمبو برس:", "max_combo_reached",
              [3, 5, 10, 20], (10, 40, 0))
_add_tier_set("critical_land", "🎯", "نشانه‌گیر", "این تعداد Critical/Headshot بزن:", "criticals_landed",
              [5, 30, 100, 400], (20, 50, 0))
_add_tier_set("reputation_gain", "🤝", "معتبر محله", "به این مقدار Reputation برس:", "reputation_reached",
              [50, 150, 300, 600], (0, 50, 1))

# چند دستاورد یکتا (بدون رده‌بندی) برای تنوع بیشتر
UNIQUE_ACHIEVEMENTS = [
    ("first_blood", "🩸", "اولین خون", "اولین کشتنت رو ثبت کن", "kills", 1, 15, 20, 0, "bronze"),
    ("broke_once", "🥀", "ته خط", "یه بار تریاک‌پوینتت صفر بشه", "went_broke", 1, 5, 0, 0, "bronze"),
    ("night_owl", "🌙", "جغد شب", "بین ساعت ۲ تا ۵ صبح تو ربات فعالیت کن", "night_activity", 1, 10, 10, 0, "bronze"),
    ("early_bird", "🌅", "زودبیدار", "بین ساعت ۵ تا ۷ صبح تو ربات فعالیت کن", "early_activity", 1, 10, 10, 0, "bronze"),
    ("perfect_blocker", "🛡", "دیوار دفاعی", "یه Perfect Block موفق ثبت کن", "perfect_blocks", 1, 20, 15, 0, "silver"),
    ("lucky_star", "🍀", "ستاره‌ی شانس", "یه Lucky Hit نادر بزن", "lucky_hits", 1, 20, 15, 0, "silver"),
    ("energy_master", "🔋", "پرانرژی", "سقف انرژیت رو حداقل یه بار ارتقا بده", "energy_upgrades", 1, 10, 10, 0, "bronze"),
    ("marketplace_debut", "🏪", "اولین معامله", "اولین خرید یا فروش تو بازار رو انجام بده", "market_transactions", 1, 5, 5, 0, "bronze"),
    ("contract_keeper", "📃", "قرارداد امضا", "اولین قرارداد تیمی رو با موفقیت تموم کن", "contracts_completed", 1, 20, 30, 0, "silver"),
    ("mini_event_lucky", "🎪", "دستِ خوش‌شانس", "تو یه Mini Event برنده شو", "mini_events_won", 1, 15, 15, 0, "silver"),
    ("skin_collector", "🎨", "کلکسیونر اسکین", "اولین Skin سلاحت رو بخر", "skins_owned", 1, 10, 10, 0, "bronze"),
    ("full_gear", "🦺", "مجهز کامل", "هر ۴ تجهیزات رو حداقل لول ۱ کن", "full_equipment_set", 1, 0, 60, 1, "gold"),
    ("veteran_week", "🗓", "یک هفته گذشت", "یک هفته از عضویتت تو ربات گذشته باشه", "days_since_join", 7, 0, 20, 0, "bronze"),
    ("veteran_month", "📆", "یک ماه گذشت", "یک ماه از عضویتت تو ربات گذشته باشه", "days_since_join", 30, 0, 60, 1, "silver"),
    ("veteran_year", "🏛", "قدیمی محله", "یک سال از عضویتت تو ربات گذشته باشه", "days_since_join", 365, 0, 300, 5, "platinum"),
    ("boss_finisher", "🗡", "ضربه‌ی نهایی", "ضربه‌ی نهایی رو به یه Boss بزن", "boss_finishing_hits", 1, 30, 40, 1, "gold"),
    ("team_founder", "🏴‍☠️", "بنیان‌گذار", "یه تیم جدید بساز", "teams_created", 1, 0, 0, 0, "bronze"),
    ("inventory_full", "🎒", "کوله سنگین", "ظرفیت کوله‌ات رو کامل پر کن", "inventory_full_times", 1, 5, 10, 0, "bronze"),
    ("streak_freezer", "🧊", "یخ‌زن حرفه‌ای", "از آیتم Freeze استریک استفاده کن", "streak_freezes_used", 1, 0, 10, 0, "bronze"),
    ("beta_tester", "🧪", "بتا تستر", "جزو اولین بازیکن‌های ربات باش", "is_early_user", 1, 0, 50, 2, "gold"),
]

ACHIEVEMENTS.extend(UNIQUE_ACHIEVEMENTS)


# ================================================================
# نشان‌ها (Badge) - بر اساس دستاوردهای خاص یا وضعیت خاص کسب میشن
# ================================================================

BADGES = [
    ("badge_killer", "💀", "قاتل حرفه‌ای", "با کشتن تعداد زیادی بازیکن به دست میاد"),
    ("badge_rich", "💰", "ثروتمند", "با رسیدن به ثروت بالا به دست میاد"),
    ("badge_dog_lover", "🐕‍🦺", "سگ‌باز", "با نگهداری و رسیدگی به چند سگ به دست میاد"),
    ("badge_legend", "👑", "لجند", "با رسیدن به لول‌های خیلی بالا به دست میاد"),
    ("badge_golden_luck", "🍀", "شانس طلا", "با رسیدن Luck به سقف به دست میاد"),
    ("badge_collector", "🗃", "کلکسیونر", "با داشتن همه سلاح‌ها یا همه اسکین‌ها به دست میاد"),
    ("badge_veteran", "🎖", "قدیمی", "با گذشت مدت طولانی از عضویت به دست میاد"),
    ("badge_beta_tester", "🧪", "بتا تستر", "مخصوص بازیکن‌های اولیه ربات"),
    ("badge_team_leader", "🏴", "رهبر تیم", "با ساختن و اداره یه تیم موفق به دست میاد"),
    ("badge_trader", "🛒", "تاجر بازار", "با معاملات زیاد تو Marketplace به دست میاد"),
    ("badge_generous", "🎁", "دست‌ودل‌باز", "با هدیه دادن زیاد به بقیه به دست میاد"),
    ("badge_boss_hunter", "👹", "غول‌کش", "با شرکت مکرر تو Boss Event به دست میاد"),
    ("badge_crafter", "🛠", "صنعتگر", "با کرفت کردن آیتم‌های زیاد به دست میاد"),
    ("badge_lucky_gambler", "🎲", "شانس‌باز", "با Lucky Hit و Critical زیاد به دست میاد"),
    ("badge_iron_wall", "🛡", "دیوار آهنی", "با Block و Perfect Block زیاد به دست میاد"),
]


# ================================================================
# متن‌های حمله متنوع هر سلاح - حداقل ۱۰ خط برای هر سلاح
# ================================================================

def _lines_for(weapon_id: str, lines: list[str]) -> list[tuple]:
    return [(weapon_id, line) for line in lines]


WEAPON_ATTACK_LINES: list[tuple] = []

WEAPON_ATTACK_LINES += _lines_for("knife", [
    "{attacker} چاقو رو کشید و زد تو بازوی {target}",
    "{target} از تیزی چاقوی {attacker} جیغ کشید",
    "{attacker} یه خط باریک رو بدن {target} انداخت",
    "چاقوی {attacker} برق زد و فرود اومد رو {target}",
    "{attacker} با یه حرکت سریع چاقو رو فرو کرد",
    "{target} نتونست از چاقوی {attacker} فرار کنه",
    "{attacker} خیلی خونسرد چاقو رو بالا برد و زد",
    "صدای پارگی لباس {target} زیر چاقوی {attacker} پیچید",
    "{attacker} یه ضربه دقیق با چاقو حواله {target} کرد",
    "چاقوی {attacker} این بار هم کار خودشو کرد",
])

WEAPON_ATTACK_LINES += _lines_for("colt", [
    "{attacker} کلت رو کشید و شلیک کرد سمت {target}",
    "صدای شلیک کلت {attacker} تو کوچه پیچید",
    "{target} از گلوله کلت {attacker} جا خورد",
    "{attacker} یه تیر دقیق با کلت زد",
    "کلت {attacker} این بار هم خطا نکرد",
    "{attacker} ماشه رو کشید و {target} رو زد",
    "{target} صدای گلوله رو قبل حس کردنش شنید",
    "{attacker} با یه دست کلت زد تو {target}",
    "دود کلت {attacker} بعد شلیک بالا رفت",
    "{attacker} خیلی سرد و بی‌تفاوت شلیک کرد",
])

WEAPON_ATTACK_LINES += _lines_for("ak47", [
    "{attacker} رگبار AK47 رو باز کرد رو {target}",
    "صدای رگبار AK47 تو کل محل پیچید",
    "{target} زیر رگبار {attacker} نتونست بمونه",
    "{attacker} با AK47 خط و نشون کشید",
    "پوکه‌های AK47 {attacker} ریختن زمین",
    "{attacker} ماشه AK47 رو تا ته کشید",
    "{target} از صدای رگبار AK47 گوشش سوت کشید",
    "{attacker} با یه رگبار کوتاه کار {target} رو ساخت",
    "AK47 {attacker} امشب هم آتیش زیادی داشت",
    "{attacker} خیلی حرفه‌ای رگبار رو کنترل کرد",
])

WEAPON_ATTACK_LINES += _lines_for("sniper", [
    "{attacker} از فاصله دور نشونه گرفت و زد تو {target}",
    "{target} حتی صدای شلیک اسنایپر {attacker} رو نشنید",
    "{attacker} یه شات تک و دقیق زد",
    "گلوله اسنایپر {attacker} مستقیم خورد به {target}",
    "{attacker} نفسشو حبس کرد و شلیک کرد",
    "{target} جایی برای فرار از تیر اسنایپر نداشت",
    "{attacker} از پشت دوربین {target} رو زد",
    "یه شات، یه نتیجه، کار اسنایپر {attacker}",
    "{target} تازه فهمید چی بهش خورد",
    "{attacker} با خونسردی کامل ماشه رو کشید",
])

# برای بقیه سلاح‌ها یه ست عمومی متنوع می‌سازیم که با اسم و ایموجی خودشون پر میشه
GENERIC_WEAPON_IDS = [
    "shotgun", "m4", "rpg", "water_gun",
]

GENERIC_TEMPLATES = [
    "{attacker} با {weapon} زد تو {target}",
    "{target} از ضربه {weapon} {attacker} جا خورد",
    "{attacker} {weapon} رو محکم کوبید رو {target}",
    "ضربه {weapon} {attacker} حسابی رو {target} نشست",
    "{attacker} این بار با {weapon} امتحان کرد رو {target}",
    "{target} زیر ضربه {weapon} {attacker} تلو تلو خورد",
    "{attacker} با یه حرکت غافلگیرکننده {weapon} رو زد",
    "صدای برخورد {weapon} {attacker} با {target} پیچید",
    "{attacker} حسابی {weapon} رو رو {target} امتحان کرد",
    "{target} انتظار همچین ضربه‌ای با {weapon} رو نداشت",
    "{attacker} با {weapon} کارشو با {target} تموم کرد",
]


async def _weapon_display_name(conn, weapon_id: str) -> str:
    cursor = await conn.execute(
        "SELECT name_fa FROM weapons WHERE weapon_id = ?", (weapon_id,)
    )
    row = await cursor.fetchone()
    return row["name_fa"] if row else weapon_id


# ================================================================
# Skill Tree ساختمان‌ها
# ================================================================

BUILDING_SKILL_BRANCHES = ["speed", "capacity", "quality", "diamond_chance"]

BUILDING_SKILL_TREE: list[tuple] = []
for building_id in ["mine", "company", "factory", "greenhouse"]:
    for branch in BUILDING_SKILL_BRANCHES:
        effect_per_level = {
            "speed": 0.05,
            "capacity": 0.08,
            "quality": 0.04,
            "diamond_chance": 0.01,
        }[branch]
        BUILDING_SKILL_TREE.append((building_id, branch, 10, effect_per_level))


# ================================================================
# مهارت‌های سگ (Dog Skills)
# ================================================================

DOG_SKILLS = [
    ("stray_scavenge", "stray", "بو کشیدن زباله", "شانس کمی برای پیدا کردن تریاک‌پوینت اضافه هنگام گشت", "passive", 3),
    ("stray_bark", "stray", "پارس ترسناک", "شانس فرار از دزدی رو کمی بالا می‌بره", "passive", 5),
    ("doberman_guard", "doberman", "نگهبان وفادار", "شانس دفاع صاحبش در برابر حمله رو افزایش می‌ده", "passive", 5),
    ("doberman_bite", "doberman", "گاز محکم", "شانس کمی برای دمیج اضافه به حمله‌کننده صاحبش", "active", 8),
    ("wolf_hunt", "wolf", "غریزه شکار", "شانس Critical صاحبش رو کمی بالا می‌بره", "passive", 10),
    ("wolf_howl", "wolf", "زوزه رهبری", "به تمام اعضای تیم صاحبش کمی Luck اضافه می‌ده", "active", 15),
]


# ================================================================
# لول لازم برای سگ/تجهیز - این‌ها روی کاتالوگ موجود UPDATE میشن
# چون INSERT OR IGNORE مقدار جدید رو به ردیف‌های از قبل موجود اضافه نمی‌کنه
# نکته: required_level ساختمان‌ها دیگه اینجا ست نمیشه، چون seed_data.py با کاتالوگ
# جدید ۴تایی (لول ۲/۴/۶/۸) این مقدار رو مستقیم و به‌روز ست می‌کنه
# ================================================================

DOG_REQUIRED_LEVELS = {
    "stray": 1,
    "doberman": 6,
    "wolf": 12,
}
# نکته: required_level تجهیزات دیگه اینجا ست نمیشه، seed_data.py مقدار درستشو ست می‌کنه


async def seed_all_v2() -> None:
    # سیستم الماس کاملاً حذف شده؛ همیشه reward_diamond رو صفر می‌کنیم و به‌جاش
    # مقدارش رو به‌صورت تریاک‌پوینت اضافه به reward_tiriak اضافه می‌کنیم تا جایزه‌ی
    # کلی کم نشه (هر واحد الماس قبلی معادل ۱۰۰ تریاک‌پوینت حساب میشه)
    achievements_no_diamond = [
        (aid, icon, title, desc, goal_type, goal_amount, reward_xp,
         reward_tiriak + reward_diamond * 100, 0, tier)
        for (aid, icon, title, desc, goal_type, goal_amount,
             reward_xp, reward_tiriak, reward_diamond, tier) in ACHIEVEMENTS
    ]
    async with get_conn() as conn:
        await conn.executemany(
            """INSERT OR IGNORE INTO achievements_catalog
               (achievement_id, icon, title, description, goal_type, goal_amount,
                reward_xp, reward_tiriak, reward_diamond, tier)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            achievements_no_diamond,
        )
        await conn.executemany(
            """INSERT OR IGNORE INTO badges_catalog (badge_id, icon, title, description)
               VALUES (?, ?, ?, ?)""",
            BADGES,
        )

        # متن‌های حمله اختصاصی که بالا تعریف شدن
        cursor = await conn.execute("SELECT weapon_id FROM weapon_attack_lines LIMIT 1")
        already_seeded = (await cursor.fetchone()) is not None

        if not already_seeded:
            await conn.executemany(
                "INSERT INTO weapon_attack_lines (weapon_id, line_text) VALUES (?, ?)",
                WEAPON_ATTACK_LINES,
            )

            # برای بقیه سلاح‌ها متن عمومی با اسم خودشون بساز
            for weapon_id in GENERIC_WEAPON_IDS:
                name = await _weapon_display_name(conn, weapon_id)
                rows = [
                    (weapon_id, template.replace("{weapon}", name))
                    for template in GENERIC_TEMPLATES
                ]
                await conn.executemany(
                    "INSERT INTO weapon_attack_lines (weapon_id, line_text) VALUES (?, ?)",
                    rows,
                )

        await conn.executemany(
            """INSERT OR IGNORE INTO building_skill_tree
               (building_id, skill_branch, max_level, effect_per_level)
               VALUES (?, ?, ?, ?)""",
            BUILDING_SKILL_TREE,
        )

        await conn.executemany(
            """INSERT OR IGNORE INTO dog_skills_catalog
               (skill_id, dog_id, name_fa, description, skill_kind, unlock_level)
               VALUES (?, ?, ?, ?, ?, ?)""",
            DOG_SKILLS,
        )

        # لول لازم برای ساختمان‌ها دیگه اینجا ست نمیشه (seed_data.py با کاتالوگ جدید ۴تایی خودش این کارو می‌کنه)
        for dog_id, req_level in DOG_REQUIRED_LEVELS.items():
            await conn.execute(
                "UPDATE dogs_catalog SET required_level = ? WHERE dog_id = ?",
                (req_level, dog_id),
            )
        # required_level تجهیزات دیگه اینجا ست نمیشه (seed_data.py با مقادیر جدید خودش این کارو می‌کنه)

        await conn.commit()
