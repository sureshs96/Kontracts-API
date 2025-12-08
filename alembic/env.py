from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool, text

from alembic import context

from dotenv import load_dotenv

load_dotenv()

# Import Base and all models to register them with metadata
from app.database import Base
from app.models import (
    Lease,
    LeaseScheduleEntry,
    LeaseClassification,
    ASC842Schedule,
    IFRS16Schedule,
    Users,
    JournalEntries,
    JournalEntrySetups,
    Payments,
    Documents,
)  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://leaseuser:leasepass@localhost:5432/leasedb")
SCHEMA_NAME = os.getenv("SCHEMA_NAME", "kontracts")

config.set_main_option('sqlalchemy.url', DATABASE_URL)
config.set_main_option('schema_name', SCHEMA_NAME)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    schema_name = config.get_main_option("schema_name", "kontracts")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema_name,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    schema_name = config.get_main_option("schema_name", "kontracts")

    with connectable.begin() as connection:
        # Create schema if it doesn't exist
        connection.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        )



    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=schema_name,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
