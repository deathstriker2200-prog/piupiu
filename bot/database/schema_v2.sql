-- ================================================================
-- Tiryaki Piu Piu - Migration v2
-- این فایل جدول‌های نسخه ۲ رو اضافه می‌کنه بدون دست زدن به schema.sql اصلی
-- هر IF NOT EXISTS داره پس اجرای دوباره‌اش هم مشکلی نداره (idempotent)
-- ================================================================

-- ستون‌های زیر (energy, luck, combo, reputation, daily login) با migration پایتونی
-- به صورت ایمن (چک قبل از افزودن) به جدول users اضافه میشن، نه اینجا
-- چون ALTER TABLE ADD COLUMN با اجرای دوباره فایل خطا میده

CREATE TABLE IF NOT EXISTS daily_login_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    streak_at_claim INTEGER NOT NULL,
    reward_tiriak   INTEGER NOT NULL DEFAULT 0,
    reward_diamond  INTEGER NOT NULL DEFAULT 0,
    used_freeze     INTEGER NOT NULL DEFAULT 0,
    claimed_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_daily_login_user ON daily_login_log(user_id);

-- --- دستاوردها (Achievement) ---
CREATE TABLE IF NOT EXISTS achievements_catalog (
    achievement_id  TEXT PRIMARY KEY,
    icon            TEXT NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    goal_type       TEXT NOT NULL,      -- attacks_made/kills/tiriak_earned/dogs_owned/... (تعریف کد داخلی)
    goal_amount     INTEGER NOT NULL,
    reward_xp       INTEGER NOT NULL DEFAULT 0,
    reward_tiriak   INTEGER NOT NULL DEFAULT 0,
    reward_diamond  INTEGER NOT NULL DEFAULT 0,
    tier            TEXT NOT NULL DEFAULT 'bronze'   -- bronze/silver/gold/platinum
);

CREATE TABLE IF NOT EXISTS user_achievements (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    achievement_id  TEXT NOT NULL REFERENCES achievements_catalog(achievement_id),
    progress        INTEGER NOT NULL DEFAULT 0,
    unlocked_at     TEXT,
    PRIMARY KEY (user_id, achievement_id)
);
CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id);

-- --- نشان‌ها (Badge) ---
CREATE TABLE IF NOT EXISTS badges_catalog (
    badge_id        TEXT PRIMARY KEY,
    icon            TEXT NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_badges (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    badge_id        TEXT NOT NULL REFERENCES badges_catalog(badge_id),
    earned_at       TEXT NOT NULL DEFAULT (datetime('now')),
    is_pinned       INTEGER NOT NULL DEFAULT 0,   -- کاربر میتونه یکی رو برای نمایش برجسته پین کنه
    PRIMARY KEY (user_id, badge_id)
);

-- --- کوله واقعی (Inventory) ---
-- این کوله شامل هر چیز قابل حمل جز سلاح/تجهیزات/غذا/سگ هست (که جدول خودشونو دارن)
-- ولی هرکدوم یه ردیف مرجع اینجا هم دارن تا جستجو/مرتب‌سازی یکجا کار کنه
CREATE TABLE IF NOT EXISTS inventory_catalog (
    inventory_item_id TEXT PRIMARY KEY,
    name_fa         TEXT NOT NULL,
    emoji           TEXT,
    category        TEXT NOT NULL,     -- material / consumable / craft_component / gift_wrap / misc
    description     TEXT,
    stack_size      INTEGER NOT NULL DEFAULT 99
);

CREATE TABLE IF NOT EXISTS user_inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    inventory_item_id TEXT NOT NULL REFERENCES inventory_catalog(inventory_item_id),
    quantity        INTEGER NOT NULL DEFAULT 0,
    acquired_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, inventory_item_id)
);
CREATE INDEX IF NOT EXISTS idx_user_inventory_user ON user_inventory(user_id);

-- ظرفیت کوله هر کاربر (مستقل، قابل ارتقا)
CREATE TABLE IF NOT EXISTS user_inventory_capacity (
    user_id         INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    capacity        INTEGER NOT NULL DEFAULT 50,
    level           INTEGER NOT NULL DEFAULT 1
);

-- --- بازار بازیکنان (Marketplace) ---
CREATE TABLE IF NOT EXISTS marketplace_listings (
    listing_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id       INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_kind       TEXT NOT NULL,      -- weapon / equipment / inventory_item / food
    item_ref_id     TEXT NOT NULL,      -- weapon_id یا equipment_id یا ...
    quantity        INTEGER NOT NULL DEFAULT 1,
    listing_type    TEXT NOT NULL DEFAULT 'fixed',  -- fixed / auction
    price           INTEGER NOT NULL,
    price_currency  TEXT NOT NULL DEFAULT 'tiriak',
    highest_bid     INTEGER,            -- برای حراج
    highest_bidder_id INTEGER,
    auction_ends_at TEXT,
    status          TEXT NOT NULL DEFAULT 'active',  -- active/sold/cancelled/expired
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_marketplace_seller ON marketplace_listings(seller_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_status ON marketplace_listings(status);

CREATE TABLE IF NOT EXISTS marketplace_sale_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id      INTEGER NOT NULL,
    seller_id       INTEGER NOT NULL,
    buyer_id        INTEGER NOT NULL,
    item_kind       TEXT NOT NULL,
    item_ref_id     TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    final_price     INTEGER NOT NULL,
    price_currency  TEXT NOT NULL,
    sold_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sale_history_seller ON marketplace_sale_history(seller_id);
CREATE INDEX IF NOT EXISTS idx_sale_history_buyer ON marketplace_sale_history(buyer_id);

-- --- هدیه (Gift) ---
CREATE TABLE IF NOT EXISTS gift_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id       INTEGER NOT NULL,
    receiver_id     INTEGER NOT NULL,
    gift_kind       TEXT NOT NULL,      -- tiriak / diamond / weapon / equipment / food / inventory_item
    gift_ref_id     TEXT,               -- برای غیر ارز، شناسه آیتم
    amount          INTEGER NOT NULL DEFAULT 1,
    sent_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_gift_log_sender ON gift_log(sender_id);
CREATE INDEX IF NOT EXISTS idx_gift_log_receiver ON gift_log(receiver_id);

-- --- قرارداد تیم (Team Contracts) ---
CREATE TABLE IF NOT EXISTS team_contracts (
    contract_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id         INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    contract_type   TEXT NOT NULL,      -- extraction / attack / income
    started_at      TEXT NOT NULL DEFAULT (datetime('now')),
    ends_at         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',  -- active/completed/broken
    reward_tiriak   INTEGER NOT NULL DEFAULT 0,
    reward_reputation INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_team_contracts_team ON team_contracts(team_id);

-- --- رویداد باس جهانی (Boss Event) ---
CREATE TABLE IF NOT EXISTS boss_events (
    boss_event_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    boss_name       TEXT NOT NULL,
    max_hp          INTEGER NOT NULL,
    current_hp      INTEGER NOT NULL,
    group_chat_id   INTEGER NOT NULL,
    started_at      TEXT NOT NULL DEFAULT (datetime('now')),
    ends_at         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',  -- active/defeated/expired
    reward_pool_tiriak INTEGER NOT NULL DEFAULT 0,
    reward_pool_diamond INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS boss_event_damage (
    boss_event_id   INTEGER NOT NULL REFERENCES boss_events(boss_event_id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total_damage    INTEGER NOT NULL DEFAULT 0,
    hits            INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (boss_event_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_boss_damage_event ON boss_event_damage(boss_event_id);

-- --- رویدادهای تصادفی (Mini Events) ---
CREATE TABLE IF NOT EXISTS mini_events_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT NOT NULL,   -- chest/money_truck/merchant/auction/diamond_rain/mine_breakdown/shop_discount
    group_chat_id   INTEGER NOT NULL,
    triggered_at    TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at     TEXT,
    winner_user_id  INTEGER,
    payload_json    TEXT             -- جزئیات آزاد رویداد (مقدار جایزه، تخفیف و غیره)
);
CREATE INDEX IF NOT EXISTS idx_mini_events_group ON mini_events_log(group_chat_id);

-- --- کرفت (Crafting) ---
CREATE TABLE IF NOT EXISTS craft_recipes (
    recipe_id       TEXT PRIMARY KEY,
    name_fa         TEXT NOT NULL,
    result_kind     TEXT NOT NULL,     -- weapon / food / ammo / inventory_item
    result_ref_id   TEXT NOT NULL,
    result_quantity INTEGER NOT NULL DEFAULT 1,
    required_level  INTEGER NOT NULL DEFAULT 1
);

-- مواد لازم برای هر رسپی (چند به یک)
CREATE TABLE IF NOT EXISTS craft_recipe_ingredients (
    recipe_id       TEXT NOT NULL REFERENCES craft_recipes(recipe_id) ON DELETE CASCADE,
    ingredient_kind TEXT NOT NULL,     -- inventory_item / food / shop_item
    ingredient_ref_id TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_kind, ingredient_ref_id)
);

CREATE TABLE IF NOT EXISTS craft_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    recipe_id       TEXT NOT NULL,
    crafted_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- --- اسکین سلاح (Skin) ---
CREATE TABLE IF NOT EXISTS weapon_skins_catalog (
    skin_id         TEXT PRIMARY KEY,
    weapon_id       TEXT NOT NULL REFERENCES weapons(weapon_id),
    name_fa         TEXT NOT NULL,
    emoji           TEXT NOT NULL,
    price           INTEGER NOT NULL,
    price_currency  TEXT NOT NULL DEFAULT 'diamond',
    has_special_text INTEGER NOT NULL DEFAULT 0,  -- آیا افکت متنی خاص خودش رو داره
    rarity          TEXT NOT NULL DEFAULT 'common'  -- common/rare/epic/legendary
);

CREATE TABLE IF NOT EXISTS user_weapon_skins (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    skin_id         TEXT NOT NULL REFERENCES weapon_skins_catalog(skin_id),
    is_equipped     INTEGER NOT NULL DEFAULT 0,
    acquired_at     TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, skin_id)
);

-- --- متن‌های حمله متنوع هر سلاح (Emoji/Attack text variety) ---
CREATE TABLE IF NOT EXISTS weapon_attack_lines (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    weapon_id       TEXT NOT NULL REFERENCES weapons(weapon_id),
    line_text       TEXT NOT NULL       -- شامل {attacker} {target} {damage} به عنوان placeholder
);
CREATE INDEX IF NOT EXISTS idx_attack_lines_weapon ON weapon_attack_lines(weapon_id);

-- کولدان اخیر متن‌های استفاده‌شده تا تکراری نشه (فقط چند تای آخر رو نگه می‌داریم)
CREATE TABLE IF NOT EXISTS user_recent_attack_lines (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    weapon_id       TEXT NOT NULL,
    line_id         INTEGER NOT NULL,
    used_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_recent_lines_user_weapon ON user_recent_attack_lines(user_id, weapon_id);

-- --- Skill Tree مستقل هر ساختمان ---
CREATE TABLE IF NOT EXISTS building_skill_tree (
    building_id     TEXT NOT NULL REFERENCES buildings_catalog(building_id),
    skill_branch    TEXT NOT NULL,     -- speed / capacity / quality / diamond_chance
    max_level       INTEGER NOT NULL DEFAULT 10,
    effect_per_level REAL NOT NULL,
    PRIMARY KEY (building_id, skill_branch)
);

CREATE TABLE IF NOT EXISTS user_building_skills (
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    building_id     TEXT NOT NULL,
    skill_branch    TEXT NOT NULL,
    level           INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, building_id, skill_branch)
);

-- ستون‌های عمق سگ (mood, hunger, sleep_level, loyalty, ...) هم با migration پایتونی اضافه میشن

CREATE TABLE IF NOT EXISTS dog_skills_catalog (
    skill_id        TEXT PRIMARY KEY,
    dog_id          TEXT NOT NULL REFERENCES dogs_catalog(dog_id),
    name_fa         TEXT NOT NULL,
    description     TEXT NOT NULL,
    skill_kind      TEXT NOT NULL,      -- active / passive
    unlock_level    INTEGER NOT NULL DEFAULT 5
);

-- --- لاگ فعالیت برای پنل ادمین ---
CREATE TABLE IF NOT EXISTS admin_activity_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id        INTEGER,            -- آیدی ادمین یا NULL برای سیستمی
    action_type     TEXT NOT NULL,      -- grant / ban / unban / item_create / event_create / rollback / restore ...
    target_id       INTEGER,
    details_json    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_admin_log_actor ON admin_activity_log(actor_id);
CREATE INDEX IF NOT EXISTS idx_admin_log_action ON admin_activity_log(action_type);

-- --- اسنپ‌شات اقتصادی برای Rollback ---
CREATE TABLE IF NOT EXISTS economy_snapshots (
    snapshot_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    tiriak_point    INTEGER NOT NULL,
    diamond         INTEGER NOT NULL,
    bank_balance    INTEGER NOT NULL,
    snapshot_reason TEXT NOT NULL,      -- مثلا 'before_admin_grant' یا 'daily_auto'
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_economy_snapshots_user ON economy_snapshots(user_id);

-- --- رویداد اختصاصی ادمین ---
CREATE TABLE IF NOT EXISTS custom_events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    description     TEXT,
    reward_tiriak   INTEGER NOT NULL DEFAULT 0,
    reward_diamond  INTEGER NOT NULL DEFAULT 0,
    reward_xp       INTEGER NOT NULL DEFAULT 0,
    starts_at       TEXT NOT NULL,
    ends_at         TEXT NOT NULL,
    created_by      INTEGER,
    status          TEXT NOT NULL DEFAULT 'scheduled'  -- scheduled/active/ended
);
