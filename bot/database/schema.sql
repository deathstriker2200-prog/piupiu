-- ================================================================
-- Tiryaki Piu Piu - دیتابیس اصلی
-- هر بخش بازی جدول مستقل خودش رو داره تا ارتقای یک بخش
-- روی بخش‌های دیگه اثر نذاره مگر جایی که صراحتاً کد شده باشه
-- ================================================================

-- کاربران اصلی
CREATE TABLE IF NOT EXISTS users (
    user_id         INTEGER PRIMARY KEY,   -- تلگرام آیدی
    username        TEXT,
    full_name       TEXT,
    hp              INTEGER NOT NULL DEFAULT 100,
    max_hp          INTEGER NOT NULL DEFAULT 100,
    level           INTEGER NOT NULL DEFAULT 1,
    xp              INTEGER NOT NULL DEFAULT 0,
    tiriak_point    INTEGER NOT NULL DEFAULT 500,
    diamond         INTEGER NOT NULL DEFAULT 0,
    kills           INTEGER NOT NULL DEFAULT 0,
    is_dead         INTEGER NOT NULL DEFAULT 0,   -- 0/1
    died_at         TEXT,                          -- ISO timestamp
    jailed_until    TEXT,                          -- ISO timestamp (دزدی ناموفق)
    is_banned       INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    last_active_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- بانک شخصی هر کاربر (سپرده امن از دست رفتن هنگام مرگ)
CREATE TABLE IF NOT EXISTS bank_accounts (
    user_id         INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    balance         INTEGER NOT NULL DEFAULT 0,
    capacity        INTEGER NOT NULL DEFAULT 1000,
    level           INTEGER NOT NULL DEFAULT 1,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- تعریف سلاح‌ها (کاتالوگ ثابت - Seed میشه)
CREATE TABLE IF NOT EXISTS weapons (
    weapon_id       TEXT PRIMARY KEY,     -- مثلا 'knife', 'ak47'
    name_fa         TEXT NOT NULL,
    emoji           TEXT NOT NULL,
    category        TEXT NOT NULL,        -- melee / firearm / fun
    damage          INTEGER NOT NULL,
    cooldown_sec    INTEGER NOT NULL,
    price           INTEGER NOT NULL DEFAULT 0,
    price_currency  TEXT NOT NULL DEFAULT 'tiriak',  -- tiriak / diamond / both
    required_level  INTEGER NOT NULL DEFAULT 1,
    needs_ammo      INTEGER NOT NULL DEFAULT 0,
    magazine_size   INTEGER,
    reload_sec      INTEGER,
    special_trait   TEXT,                 -- توضیح ویژگی خاص (متنی/کد داخلی)
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- سلاح‌هایی که هر کاربر مالکشه
CREATE TABLE IF NOT EXISTS user_weapons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    weapon_id       TEXT NOT NULL REFERENCES weapons(weapon_id),
    ammo_current    INTEGER NOT NULL DEFAULT 0,
    is_equipped     INTEGER NOT NULL DEFAULT 0,
    acquired_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, weapon_id)
);

-- کولدان حمله هر کاربر با هر سلاح (مستقل از بقیه کولدان‌ها)
CREATE TABLE IF NOT EXISTS attack_cooldowns (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    weapon_id       TEXT NOT NULL,
    available_at    TEXT NOT NULL,        -- ISO timestamp
    PRIMARY KEY (user_id, weapon_id)
);

-- سگ‌ها (کاتالوگ ثابت)
CREATE TABLE IF NOT EXISTS dogs_catalog (
    dog_id          TEXT PRIMARY KEY,     -- 'stray', 'doberman', 'wolf'
    name_fa         TEXT NOT NULL,
    emoji           TEXT NOT NULL,
    power           INTEGER NOT NULL,
    hp              INTEGER NOT NULL,
    defense_chance  REAL NOT NULL,        -- 0.0 - 1.0
    income_per_hour INTEGER NOT NULL,
    price           INTEGER NOT NULL,
    price_currency  TEXT NOT NULL DEFAULT 'tiriak'
);

-- سگ‌های متعلق به هر کاربر
CREATE TABLE IF NOT EXISTS user_dogs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    dog_id          TEXT NOT NULL REFERENCES dogs_catalog(dog_id),
    nickname        TEXT,
    dog_level       INTEGER NOT NULL DEFAULT 1,
    dog_xp          INTEGER NOT NULL DEFAULT 0,
    last_fed_at     TEXT,
    acquired_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- کاتالوگ غذا
CREATE TABLE IF NOT EXISTS food_catalog (
    food_id         TEXT PRIMARY KEY,     -- 'bone', 'meat', 'canned', 'steak'
    name_fa         TEXT NOT NULL,
    emoji           TEXT NOT NULL,
    xp_amount       INTEGER NOT NULL,
    price           INTEGER NOT NULL,
    price_currency  TEXT NOT NULL DEFAULT 'tiriak'
);

-- موجودی غذای کاربر
CREATE TABLE IF NOT EXISTS user_food_inventory (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    food_id         TEXT NOT NULL REFERENCES food_catalog(food_id),
    quantity        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, food_id)
);

-- تجهیزات (کاتالوگ)
CREATE TABLE IF NOT EXISTS equipment_catalog (
    equipment_id    TEXT PRIMARY KEY,     -- 'vest', 'helmet', 'boots', 'gloves'
    name_fa         TEXT NOT NULL,
    emoji           TEXT NOT NULL,
    slot            TEXT NOT NULL         -- vest/helmet/boots/gloves
);

-- تجهیزات کاربر با لول مستقل هر کدام
CREATE TABLE IF NOT EXISTS user_equipment (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    equipment_id    TEXT NOT NULL REFERENCES equipment_catalog(equipment_id),
    level           INTEGER NOT NULL DEFAULT 0,   -- 0 = هنوز نخریده
    PRIMARY KEY (user_id, equipment_id)
);

-- ساختمان‌ها (کاتالوگ)
CREATE TABLE IF NOT EXISTS buildings_catalog (
    building_id     TEXT PRIMARY KEY,     -- 'mine', 'company', 'factory', ...
    name_fa         TEXT NOT NULL,
    emoji           TEXT NOT NULL,
    effect_type     TEXT NOT NULL,        -- income / gang_damage / bank_interest / ...
    base_value      REAL NOT NULL,        -- مقدار پایه اثر در لول ۱
    value_growth    REAL NOT NULL DEFAULT 1.1  -- ضریب رشد اثر به ازای هر لول
);

-- ساختمان‌های کاربر با لول مستقل
CREATE TABLE IF NOT EXISTS user_buildings (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    building_id     TEXT NOT NULL REFERENCES buildings_catalog(building_id),
    level           INTEGER NOT NULL DEFAULT 0,
    last_collected_at TEXT,
    PRIMARY KEY (user_id, building_id)
);

-- تیم‌ها
CREATE TABLE IF NOT EXISTS teams (
    team_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    logo_emoji      TEXT,
    description     TEXT,
    capacity        INTEGER NOT NULL DEFAULT 10,
    owner_id        INTEGER NOT NULL REFERENCES users(user_id),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ارتقاهای مستقل تیم (هر خط یک نوع ارتقا)
CREATE TABLE IF NOT EXISTS team_upgrades (
    team_id         INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    upgrade_type    TEXT NOT NULL,        -- damage / hp / income / capacity
    level           INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (team_id, upgrade_type)
);

-- عضویت اعضای تیم
CREATE TABLE IF NOT EXISTS team_members (
    team_id         INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role            TEXT NOT NULL DEFAULT 'member',  -- owner / member
    joined_at       TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (team_id, user_id)
);

-- درخواست‌های عضویت تیم در انتظار
CREATE TABLE IF NOT EXISTS team_join_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id         INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'pending', -- pending/accepted/rejected
    requested_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- کوئست‌ها (تعریف)
CREATE TABLE IF NOT EXISTS quests (
    quest_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    period          TEXT NOT NULL,        -- daily/weekly/monthly
    goal_type       TEXT NOT NULL,        -- attacks/kills/feed_dog/buy_item/upgrade_building
    goal_amount     INTEGER NOT NULL,
    reward_xp       INTEGER NOT NULL DEFAULT 0,
    reward_tiriak   INTEGER NOT NULL DEFAULT 0,
    reward_diamond  INTEGER NOT NULL DEFAULT 0,
    is_active       INTEGER NOT NULL DEFAULT 1
);

-- پیشرفت کاربر روی هر کوئست
CREATE TABLE IF NOT EXISTS user_quest_progress (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    quest_id        INTEGER NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    progress        INTEGER NOT NULL DEFAULT 0,
    is_completed    INTEGER NOT NULL DEFAULT 0,
    period_start    TEXT NOT NULL,        -- برای بازنشانی دوره‌ای
    PRIMARY KEY (user_id, quest_id, period_start)
);

-- لاگ حمله‌ها (تاریخچه - برای آمار/لیدربرد/دیباگ)
CREATE TABLE IF NOT EXISTS attack_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    attacker_id     INTEGER NOT NULL,
    target_id       INTEGER NOT NULL,
    weapon_id       TEXT NOT NULL,
    damage_dealt    INTEGER NOT NULL,
    tiriak_stolen   INTEGER NOT NULL DEFAULT 0,
    target_died     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- لاگ دزدی
CREATE TABLE IF NOT EXISTS theft_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    thief_id        INTEGER NOT NULL,
    target_id       INTEGER NOT NULL,
    success         INTEGER NOT NULL,
    amount_stolen   INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- تنظیمات قابل تغییر از پنل ادمین (override مقادیر game_config.py)
CREATE TABLE IF NOT EXISTS settings_overrides (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- آیتم‌های عمومی فروشگاه که در دسته‌های بالا جا نمیشن (drop ها و غیره)
CREATE TABLE IF NOT EXISTS shop_items (
    item_id         TEXT PRIMARY KEY,
    name_fa         TEXT NOT NULL,
    emoji           TEXT,
    category        TEXT NOT NULL,
    price           INTEGER NOT NULL,
    price_currency  TEXT NOT NULL DEFAULT 'tiriak',
    effect_json     TEXT,                 -- JSON آزاد برای اثر آیتم
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS user_items (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_id         TEXT NOT NULL REFERENCES shop_items(item_id),
    quantity        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_users_level ON users(level DESC);
CREATE INDEX IF NOT EXISTS idx_users_xp ON users(xp DESC);
CREATE INDEX IF NOT EXISTS idx_users_tiriak ON users(tiriak_point DESC);
CREATE INDEX IF NOT EXISTS idx_users_kills ON users(kills DESC);
CREATE INDEX IF NOT EXISTS idx_attack_logs_target ON attack_logs(target_id);
