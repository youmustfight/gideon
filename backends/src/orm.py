import env

# MIGRATION CONFIG
TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{env.env_get_database_app_user_name()}:{env.env_get_database_app_user_password()}@{env.env_get_database_app_host()}:{env.env_get_database_app_port()}/{env.env_get_database_app_name()}"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
# MIGRATION COMMANDS
# 1. ran 'aerich init-db' to setup our first model (aka an automatically spec'd migraiton file)
# 2. ran 'aerich migrate --name xyz' to create new migration file
# 3. ran 'aerich upgrade' to actually run the new migration file