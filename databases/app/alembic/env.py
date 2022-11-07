from alembic import context
from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os

# SETUP
# --- alembic context
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
target_metadata = None
# --- env (copied from backends/env.py)
load_dotenv("../../.env")
def env_get_database_app_user_name():
  return os.environ['DATABASE_APP_USER_NAME']
def env_get_database_app_user_password():
  return os.environ['DATABASE_APP_USER_PASSWORD']
def env_get_database_app_name():
  return os.environ['DATABASE_APP_NAME']
def env_get_database_app_host():
  return os.environ['DATABASE_APP_HOST']
def env_get_database_app_port():
  return os.environ['DATABASE_APP_PORT']
def env_get_database_app_url():
  return f"postgresql+psycopg2://{env_get_database_app_user_name()}:{env_get_database_app_user_password()}@{env_get_database_app_host()}:{env_get_database_app_port()}/{env_get_database_app_name()}"


# RUNNER (keeping life simple w/ sync)
def run_migrations() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # setting url via hack via https://github.com/sqlalchemy/alembic/issues/606#issuecomment-537729908
    config_section = config.get_section(config.config_ini_section)
    config_section["sqlalchemy.url"] = env_get_database_app_url()
    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# EXEC
# 1. alembic revision -m "create account table"
# 2. "alembic upgrade head" or "alembic upgrade +1" or "alembic downgrade -1"
run_migrations()

