import os
import secrets

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.schemas import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.models.user import User
from app.models.password_reset_token import PasswordResetToken

import app.core.security

from app.core.security import (
    verify_password,
    create_access_token
)

from app.services.email_service import (
    send_password_reset_email
)


router = APIRouter()


# Register
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


# Login
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
        str(user.password)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Create Access Token
    access_token = create_access_token(
        {
            "sub": user.email
        }
    )

    # Login Response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
        "email": user.email
    }


# Forgot Password
@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # Always return the same response.
    # This prevents revealing whether an email is registered.
    if not user:
        return {
            "message": "If an account exists with this email, "
                       "a password reset link has been sent."
        }

    # Remove previous unused reset tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == "false"
    ).delete()

    # Generate a cryptographically secure token
    reset_token = secrets.token_urlsafe(32)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    password_reset = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used="false"
    )

    db.add(password_reset)
    db.commit()

    # Frontend reset-password page
    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    reset_link = (
        f"{frontend_url}/reset-password"
        f"?token={reset_token}"
    )

    send_password_reset_email(
        recipient_email=user.email,
        reset_link=reset_link
    )

    return {
        "message": "If an account exists with this email, "
                   "a password reset link has been sent."
    }


# Reset Password
@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    reset_record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == request.token,
            PasswordResetToken.used == "false"
        )
        .first()
    )

    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link."
        )

    # Make both datetimes timezone-aware for comparison
    expires_at = reset_record.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if datetime.now(timezone.utc) > expires_at:
        reset_record.used = "true"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link."
        )

    user = (
        db.query(User)
        .filter(User.id == reset_record.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset request."
        )

    # Hash the new password
    user.password = app.core.security.hash_password(
        request.new_password
    )

    # Invalidate the reset token
    reset_record.used = "true"

    db.commit()

    return {
        "message": "Password reset successfully. "
                   "You can now login with your new password."
    }