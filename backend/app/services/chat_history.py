from app.database.database import SessionLocal
from app.models.chat_message import ChatMessage


# ==========================================
# Save Chat Message
# ==========================================

def add_message(user_id, role, content):

    db = SessionLocal()

    try:

        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content
        )

        db.add(message)

        db.commit()

        print(
            f"Saved chat message: user_id={user_id}, role={role}"
        )

    finally:
        db.close()


# ==========================================
# Get Chat History
# ==========================================

def get_history(user_id, limit=10):

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
            f"Loaded chat history: user_id={user_id}, "
            f"messages={len(messages)}"
        )

        return [
            {
                "role": message.role,
                "content": message.content
            }
            for message in messages
        ]

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

    finally:

        db.close()