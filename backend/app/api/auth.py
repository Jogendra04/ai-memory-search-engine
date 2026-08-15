from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.schemas import RegisterRequest
from app.models.schemas import LoginRequest
from app.models.user import User

import app.core.security

from app.core.security import (
    verify_password,
    create_access_token
)


router = APIRouter()


# ==========================================
# Register
# ==========================================

@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )


    hashed_password = app.core.security.hash_password(
        request.password
    )


    user = User(
        name=request.name,
        email=request.email,
        password=hashed_password
    )


    db.add(user)

    db.commit()

    db.refresh(user)


    return {
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# ==========================================
# Login
# ==========================================

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    if not verify_password(
        request.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    # ======================================
    # Create Access Token
    # ======================================

    access_token = create_access_token(
        {
            "sub": user.email
        }
    )


    # ======================================
    # Login Response
    # ======================================

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
        "email": user.email
    }