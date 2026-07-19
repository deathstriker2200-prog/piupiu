from bot.database.repositories import team_repo, user_repo

TEAM_CREATE_COST = 5000


class TeamError(Exception):
    pass


UPGRADE_EFFECTS = {
    "damage": 0.05,     # +5% به ازای هر لول
    "hp": 0.03,         # +3% به ازای هر لول
    "income": 0.10,     # +10% به ازای هر لول
    "capacity": 5,       # +5 نفر ظرفیت به ازای هر لول
}

UPGRADE_COST_BASE = 3000


async def create_team(owner_id: int, name: str, logo_emoji: str, description: str) -> int:
    existing = await team_repo.get_user_team(owner_id)
    if existing is not None:
        raise TeamError("already_in_team")

    existing_name = await team_repo.get_team_by_name(name)
    if existing_name is not None:
        raise TeamError("name_taken")

    user = await user_repo.get_user(owner_id)
    if user is None or user.tiriak_point < TEAM_CREATE_COST:
        raise TeamError("not_enough_money")

    await user_repo.adjust_tiriak(owner_id, -TEAM_CREATE_COST)
    return await team_repo.create_team(name, owner_id, logo_emoji, description)


async def request_join(user_id: int, team_id: int) -> int:
    existing = await team_repo.get_user_team(user_id)
    if existing is not None:
        raise TeamError("already_in_team")

    team = await team_repo.get_team(team_id)
    if team is None:
        raise TeamError("team_not_found")

    members = await team_repo.get_team_members(team_id)
    if len(members) >= team.capacity:
        raise TeamError("team_full")

    return await team_repo.create_join_request(team_id, user_id)


async def respond_to_request(request_id: int, accept: bool) -> dict:
    request = await team_repo.get_join_request(request_id)
    if request is None or request["status"] != "pending":
        raise TeamError("invalid_request")

    if accept:
        await team_repo.add_member(request["team_id"], request["user_id"])
        await team_repo.update_join_request_status(request_id, "accepted")
    else:
        await team_repo.update_join_request_status(request_id, "rejected")

    team = await team_repo.get_team(request["team_id"])
    return {"team_name": team.name if team else "", "user_id": request["user_id"], "accepted": accept}


async def leave_team(user_id: int) -> None:
    team = await team_repo.get_user_team(user_id)
    if team is None:
        raise TeamError("not_in_team")
    if team.owner_id == user_id:
        raise TeamError("owner_cannot_leave")
    await team_repo.remove_member(team.team_id, user_id)


async def upgrade_team(team_id: int, upgrade_type: str) -> int:
    if upgrade_type not in UPGRADE_EFFECTS:
        raise TeamError("invalid_upgrade_type")

    current_level = await team_repo.get_team_upgrade_level(team_id, upgrade_type)
    cost = UPGRADE_COST_BASE * (current_level + 1)

    team = await team_repo.get_team(team_id)
    if team is None:
        raise TeamError("team_not_found")

    owner = await user_repo.get_user(team.owner_id)
    if owner is None or owner.tiriak_point < cost:
        raise TeamError("not_enough_money")

    await user_repo.adjust_tiriak(team.owner_id, -cost)
    new_level = current_level + 1
    await team_repo.set_team_upgrade_level(team_id, upgrade_type, new_level)
    return new_level
