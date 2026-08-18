import json
from datetime import datetime, date

from app.database.database import SessionLocal
from app.models.chat_message import ChatMessage


# Save Chat Message

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
            ),
            created_at=datetime.utcnow()
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


# Get Today's Chat History

def get_history(
    user_id,
    limit=50
):

    db = SessionLocal()

    try:

        today = date.today()

        start_of_day = datetime.combine(
            today,
            datetime.min.time()
        )

        end_of_day = datetime.combine(
            today,
            datetime.max.time()
        )

        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.created_at >= start_of_day,
                ChatMessage.created_at <= end_of_day
            )
            .order_by(
                ChatMessage.id.asc()
            )
            .limit(limit)
            .all()
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

        print(
            f"Loaded today's chat history: "
            f"user_id={user_id}, "
            f"messages={len(history)}"
        )

        return history

    finally:

        db.close()


# Clear Chat History

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