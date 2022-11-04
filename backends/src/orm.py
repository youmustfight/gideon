import env

# DB CONFIGS
ORM_CONFIG = {
    "connections": {
        # https://github.com/tortoise/tortoise-orm/blob/main/docs/databases.rst#db_url
        "default": f"postgresql+asyncpg://{env.env_get_database_app_user_name()}:{env.env_get_database_app_user_password()}@{env.env_get_database_app_host()}:{env.env_get_database_app_port()}/{env.env_get_database_app_name()}"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

# TORTOISE 
# seems we want to use Sanic's plugin for tortise-orm so they share the event loop...?
# async def init_tortise():
#     await Tortoise.init(
#         db_url=ORM_CONFIG["connections"]["default"],
#         modules={'models': ["models"]}
#     )
#     # Generate the schema
#     await Tortoise.generate_schemas()

# MIGRATION COMMANDS
# 1. ran 'aerich init-db' to setup our first model (aka an automatically spec'd migraiton file)
# 2. ran 'aerich migrate --name xyz' to create new migration file
# 3. ran 'aerich upgrade' to actually run the new migration file

