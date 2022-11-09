from dotenv import load_dotenv
import os
# load .env in case we're running via command line and don't have docker loading in env
load_dotenv("../../.env")

# DATABASE
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
def env_get_database_app_url(driver="asyncpg"):
  return f"postgresql+{driver}://{env_get_database_app_user_name()}:{env_get_database_app_user_password()}@{env_get_database_app_host()}:{env_get_database_app_port()}/{env_get_database_app_name()}"
def env_get_database_pinecone_api_key():
  return os.environ['DATABASE_PINECONE_API_KEY']
def env_get_database_pinecone_environment():
  return os.environ['DATABASE_PINECONE_ENVIRONMENT']
