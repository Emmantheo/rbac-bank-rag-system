def normalize_roles(roles: list[str] | str) -> list[str]:
    if isinstance(roles, list):
        return [role.strip().lower() for role in roles if role and role.strip()]
    return [role.strip().lower() for role in roles.split(',') if role and role.strip()]


def has_access(user_role: str, allowed_roles: list[str] | str) -> bool:
    return user_role.strip().lower() in normalize_roles(allowed_roles)
