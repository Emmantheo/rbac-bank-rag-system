from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from models.role import Role
from models.user import User


DEFAULT_ROLES = [
    "admin",
    "compliance",
    "legal",
    "risk",
    "auditor",
]


def seed_roles(db: Session) -> None:
    for role_name in DEFAULT_ROLES:
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if not existing_role:
            db.add(Role(name=role_name, description=f"{role_name} role"))
    db.commit()


def get_roles(db: Session) -> list[Role]:
    return db.query(Role).order_by(Role.name.asc()).all()


def register_user(
    db: Session,
    full_name: str,
    email: str,
    username: str,
    password: str,
    role: str,
) -> tuple[str, User]:
    normalized_username = username.strip().lower()
    normalized_email = email.strip().lower()
    normalized_role = role.strip().lower()

    existing_user_by_username = db.query(User).filter(User.username == normalized_username).first()
    if existing_user_by_username:
        raise ValueError("username already exists")

    existing_user_by_email = db.query(User).filter(User.email == normalized_email).first()
    if existing_user_by_email:
        raise ValueError("email already exists")

    existing_role = db.query(Role).filter(Role.name == normalized_role).first()
    if not existing_role:
        raise ValueError("selected role does not exist")

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        username=normalized_username,
        password_hash=hash_password(password),
        role_name=normalized_role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role_name,
            "email": user.email,
        }
    )
    return token, user


def login_user(db: Session, username: str, password: str) -> tuple[str, User]:
    normalized_username = username.strip().lower()

    user = db.query(User).filter(User.username == normalized_username).first()
    if not user:
        raise ValueError("invalid username or password")

    if not verify_password(password, user.password_hash):
        raise ValueError("invalid username or password")

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role_name,
            "email": user.email,
        }
    )
    return token, user