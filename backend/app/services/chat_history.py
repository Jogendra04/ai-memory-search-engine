import json
from datetime import datetime, date, timezone

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
            sources=json.dumps(sources or []),
            created_at=datetime.now(timezone.utc)
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        print(
            f"Saved chat message: "
            f"user_id={user_id}, "
            f"role={role}"
        )

        return message

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Get Today's Chat History

def get_history(
    user_id,
    limit=50
):
    db = SessionLocal()

    try:
        # Make sure limit is valid
        if limit <= 0:
            limit = 50

        today = date.today()

        start_of_day = datetime.combine(
            today,
            datetime.min.time()
        ).replace(tzinfo=timezone.utc)

        end_of_day = datetime.combine(
            today,
            datetime.max.time()
        ).replace(tzinfo=timezone.utc)

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
                    json.loads(str(message.sources))
                    if message.sources is not None
                    else []
                )

            except (json.JSONDecodeError, TypeError):
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

        deleted_count = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id
            )
            .delete(
                synchronize_session=False
            )
        )

        db.commit()

        print(
            f"Cleared chat history: "
            f"user_id={user_id}, "
            f"messages={deleted_count}"
        )

        return deleted_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()