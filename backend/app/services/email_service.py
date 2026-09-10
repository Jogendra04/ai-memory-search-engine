import os
from typing import Any, cast

try:
    import resend  # type: ignore[import-not-found]
except ImportError:
    resend = None  # type: ignore[assignment]

from fastapi import HTTPException
from dotenv import load_dotenv


load_dotenv()


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")


def send_password_reset_email(
    recipient_email: str,
    reset_link: str
):
    if not RESEND_API_KEY or not FROM_EMAIL or resend is None:
        raise HTTPException(
            status_code=500,
            detail="Email service is not configured."
        )

    resend.api_key = RESEND_API_KEY

    params: dict[str, Any] = {
        "from": FROM_EMAIL,
        "to": [recipient_email],
        "subject": "Reset your AI Memory Search password",
        "html": f"""
        <html>
            <body>
                <h2>Password Reset</h2>

                <p>
                    We received a request to reset your
                    AI Memory Search password.
                </p>

                <p>
                    Click the button below to create a new password:
                </p>

                <p>
                    <a
                        href="{reset_link}"
                        style="
                            display:inline-block;
                            padding:12px 20px;
                            background:#2563eb;
                            color:white;
                            text-decoration:none;
                            border-radius:6px;
                        "
                    >
                        Reset Password
                    </a>
                </p>

                <p>
                    This link will expire in 30 minutes.
                </p>

                <p>
                    If you did not request a password reset,
                    you can safely ignore this email.
                </p>
            </body>
        </html>
        """
    }

    try:
        resend.Emails.send(cast(Any, params))

    except Exception as error:
        print("Email sending error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to send password reset email."
        )