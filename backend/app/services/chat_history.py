import json

from app.database.database import SessionLocal
from app.models.chat_message import ChatMessage


# ==========================================
# Save Chat Message
# ==========================================

def add_message(
    user_id,
    role,
    content,
    sources=None
):

    db = SessionLocal()

    try:

        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content,
            sources=json.dumps(
                sources or []
            )
        )

        db.add(message)

        db.commit()

        print(
            f"Saved chat message: "
            f"user_id={user_id}, "
            f"role={role}"
        )

    finally:

        db.close()


# ==========================================
# Get Chat History
# ==========================================

def get_history(
    user_id,
    limit=50
):

    db = SessionLocal()

    try:

        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id
            )
            .order_by(
                ChatMessage.id.desc()
            )
            .limit(limit)
            .all()
        )

        messages.reverse()

        print(
            f"Loaded chat history: "
            f"user_id={user_id}, "
            f"messages={len(messages)}"
        )

        history = []

        for message in messages:

            try:

                sources = (
                    json.loads(
                        message.sources
                    )
                    if message.sources
                    else []
                )

            except json.JSONDecodeError:

                sources = []

            history.append(
                {
                    "role": message.role,
                    "content": message.content,
                    "sources": sources
                }
            )

        return history

    finally:

        db.close()


# ==========================================
# Clear Chat History
# ==========================================

def clear_history(user_id):
    """
    Remove all chat history
    for a specific user.
    """

    db = SessionLocal()

    try:

        db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).delete()

        db.commit()

        print(
            f"Cleared chat history: "
            f"user_id={user_id}"
        )

    finally:

        db.close()