from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RoleResponse,
)
from services.auth import get_roles, login_user, register_user

router = APIRouter()


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)) -> list[RoleResponse]:
    roles = get_roles(db=db)
    return [
        RoleResponse(name=role.name, description=role.description)
        for role in roles
    ]


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    try:
        token, user = register_user(
            db=db,
            full_name=payload.full_name,
            email=payload.email,
            username=payload.username,
            password=payload.password,
            role=payload.role,
        )
        return RegisterResponse(
            access_token=token,
            user={
                "full_name": user.full_name,
                "email": user.email,
                "username": user.username,
                "role": user.role_name,
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        token, user = login_user(
            db=db,
            username=payload.username,
            password=payload.password,
        )
        return LoginResponse(
            access_token=token,
            user={
                "full_name": user.full_name,
                "email": user.email,
                "username": user.username,
                "role": user.role_name,
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc