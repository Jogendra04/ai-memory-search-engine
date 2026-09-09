from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv

from app.database.database import Base
from app.models.user import User
from app.models.chat_message import ChatMessage

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_database_url() -> str:
    database_url = os.getenv("POSTGRES_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "POSTGRES_DATABASE_URL is not configured."
        )

    # Explicitly use psycopg 3
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


database_url: str = get_database_url()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()