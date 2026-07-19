from bot.database.db import get_conn


async def get_user_stats(user_id: int) -> dict:
    """آمار کامل یک کاربر برای نمایش تو پروفایل"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) as c, COALESCE(SUM(damage_dealt),0) as dmg, COALESCE(SUM(tiriak_stolen),0) as stolen "
            "FROM attack_logs WHERE attacker_id = ?",
            (user_id,),
        )
        attack_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM attack_logs WHERE attacker_id = ? AND target_died = 1",
            (user_id,),
        )
        kills_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM attack_logs WHERE target_id = ?",
            (user_id,),
        )
        times_attacked_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM attack_logs WHERE target_id = ? AND target_died = 1",
            (user_id,),
        )
        deaths_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c, COALESCE(SUM(amount_stolen),0) as amt FROM theft_logs "
            "WHERE thief_id = ? AND success = 1",
            (user_id,),
        )
        theft_success_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM theft_logs WHERE thief_id = ? AND success = 0",
            (user_id,),
        )
        theft_fail_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM user_weapons WHERE user_id = ?", (user_id,)
        )
        weapons_owned_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM user_dogs WHERE user_id = ?", (user_id,)
        )
        dogs_owned_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COALESCE(SUM(level),0) as s FROM user_buildings WHERE user_id = ?",
            (user_id,),
        )
        buildings_level_row = await cursor.fetchone()

        # رتبه کاربر بر اساس لول (بین بازیکن‌های بن‌نشده)
        cursor = await conn.execute(
            "SELECT COUNT(*) + 1 as rank FROM users "
            "WHERE is_banned = 0 AND (level > (SELECT level FROM users WHERE user_id = ?) "
            "OR (level = (SELECT level FROM users WHERE user_id = ?) AND xp > (SELECT xp FROM users WHERE user_id = ?)))",
            (user_id, user_id, user_id),
        )
        rank_row = await cursor.fetchone()

        cursor = await conn.execute("SELECT COUNT(*) as c FROM users WHERE is_banned = 0")
        total_players_row = await cursor.fetchone()

    total_attacks = attack_row["c"]
    kills = kills_row["c"]

    return {
        "attacks_made": total_attacks,
        "total_damage_dealt": attack_row["dmg"],
        "tiriak_stolen_in_combat": attack_row["stolen"],
        "kills": kills,
        "win_rate": round((kills / total_attacks * 100), 1) if total_attacks else 0.0,
        "times_attacked": times_attacked_row["c"],
        "deaths": deaths_row["c"],
        "theft_success_count": theft_success_row["c"],
        "theft_success_amount": theft_success_row["amt"],
        "theft_fail_count": theft_fail_row["c"],
        "weapons_owned": weapons_owned_row["c"],
        "dogs_owned": dogs_owned_row["c"],
        "buildings_total_level": buildings_level_row["s"],
        "rank": rank_row["rank"],
        "total_players": total_players_row["c"],
    }


async def get_global_stats() -> dict:
    """آمار کلی بازی برای پنل ادمین"""
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT COUNT(*) as c FROM users")
        total_users = (await cursor.fetchone())["c"]

        cursor = await conn.execute("SELECT COUNT(*) as c FROM users WHERE is_banned = 1")
        banned_users = (await cursor.fetchone())["c"]

        cursor = await conn.execute("SELECT COUNT(*) as c FROM users WHERE is_dead = 1")
        dead_now = (await cursor.fetchone())["c"]

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM users WHERE jailed_until IS NOT NULL"
        )
        jailed_now = (await cursor.fetchone())["c"]

        cursor = await conn.execute("SELECT COUNT(*) as c FROM teams")
        total_teams = (await cursor.fetchone())["c"]

        cursor = await conn.execute("SELECT COUNT(*) as c FROM attack_logs")
        total_attacks = (await cursor.fetchone())["c"]

        cursor = await conn.execute("SELECT COUNT(*) as c FROM attack_logs WHERE target_died = 1")
        total_kills = (await cursor.fetchone())["c"]

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM theft_logs WHERE success = 1"
        )
        total_theft_success = (await cursor.fetchone())["c"]

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM theft_logs WHERE success = 0"
        )
        total_theft_fail = (await cursor.fetchone())["c"]

        cursor = await conn.execute(
            "SELECT COALESCE(SUM(tiriak_point),0) as s FROM users"
        )
        total_tiriak_in_economy = (await cursor.fetchone())["s"]

        cursor = await conn.execute(
            "SELECT COALESCE(SUM(balance),0) as s FROM bank_accounts"
        )
        total_bank_balance = (await cursor.fetchone())["s"]

        cursor = await conn.execute("SELECT COUNT(*) as c FROM user_dogs")
        total_dogs = (await cursor.fetchone())["c"]

        cursor = await conn.execute(
            "SELECT weapon_id, COUNT(*) as c FROM user_weapons GROUP BY weapon_id ORDER BY c DESC LIMIT 1"
        )
        top_weapon_row = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT AVG(level) as avg_level FROM users WHERE is_banned = 0"
        )
        avg_level_row = await cursor.fetchone()

    return {
        "total_users": total_users,
        "banned_users": banned_users,
        "dead_now": dead_now,
        "jailed_now": jailed_now,
        "total_teams": total_teams,
        "total_attacks": total_attacks,
        "total_kills": total_kills,
        "total_theft_success": total_theft_success,
        "total_theft_fail": total_theft_fail,
        "total_tiriak_in_economy": total_tiriak_in_economy,
        "total_bank_balance": total_bank_balance,
        "total_dogs": total_dogs,
        "top_weapon": top_weapon_row["weapon_id"] if top_weapon_row else None,
        "avg_level": round(avg_level_row["avg_level"], 1) if avg_level_row and avg_level_row["avg_level"] else 0,
    }
