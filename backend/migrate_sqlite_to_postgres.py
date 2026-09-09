import sqlite3
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# ---------------------------------------------------------
# DATABASE CONNECTIONS
# ---------------------------------------------------------

SQLITE_DB = "memory.db"

POSTGRES_URL = os.getenv("POSTGRES_DATABASE_URL")

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_DATABASE_URL is not configured.")

if POSTGRES_URL.startswith("postgresql://"):
    POSTGRES_URL = POSTGRES_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

postgres_engine = create_engine(
    POSTGRES_URL,
    pool_pre_ping=True
)

# ---------------------------------------------------------
# READ SQLITE DATA
# ---------------------------------------------------------

sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row

sqlite_cursor = sqlite_conn.cursor()

users = sqlite_cursor.execute(
    "SELECT id, name, email, password FROM users"
).fetchall()

chat_messages = sqlite_cursor.execute(
    """
    SELECT id, user_id, role, content, sources, created_at
    FROM chat_messages
    """
).fetchall()

print(f"Found {len(users)} users in SQLite.")
print(f"Found {len(chat_messages)} chat messages in SQLite.")

# ---------------------------------------------------------
# MIGRATE TO POSTGRES
# ---------------------------------------------------------

with postgres_engine.begin() as pg:

    # -------------------------
    # USERS
    # -------------------------

    for user in users:
        existing_user = pg.execute(
            text("SELECT id FROM users WHERE id = :id"),
            {"id": user["id"]}
        ).fetchone()

        if existing_user:
            print(f"User already exists, skipping: {user['email']}")
            continue

        pg.execute(
            text(
                """
                INSERT INTO users (id, name, email, password)
                VALUES (:id, :name, :email, :password)
                """
            ),
            {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "password": user["password"],
            }
        )

        print(f"Migrated user: {user['email']}")

    # -------------------------
    # CHAT MESSAGES
    # -------------------------

    for message in chat_messages:
        existing_message = pg.execute(
            text("SELECT id FROM chat_messages WHERE id = :id"),
            {"id": message["id"]}
        ).fetchone()

        if existing_message:
            continue

        created_at = message["created_at"]

        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                ).replace(tzinfo=None)
            except ValueError:
                created_at = datetime.utcnow()

        pg.execute(
            text(
                """
                INSERT INTO chat_messages
                (id, user_id, role, content, sources, created_at)
                VALUES
                (:id, :user_id, :role, :content, :sources, :created_at)
                """
            ),
            {
                "id": message["id"],
                "user_id": message["user_id"],
                "role": message["role"],
                "content": message["content"],
                "sources": message["sources"],
                "created_at": created_at,
            }
        )

print("\nMigration completed successfully.")

# ---------------------------------------------------------
# CLOSE SQLITE
# ---------------------------------------------------------

sqlite_conn.close()

# ---------------------------------------------------------
# VERIFY POSTGRES
# ---------------------------------------------------------

with postgres_engine.connect() as pg:
    user_count = pg.execute(
        text("SELECT COUNT(*) FROM users")
    ).scalar()

    message_count = pg.execute(
        text("SELECT COUNT(*) FROM chat_messages")
    ).scalar()

print("\nSupabase verification:")
print(f"Users: {user_count}")
print(f"Chat messages: {message_count}")