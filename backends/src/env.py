from dotenv import load_dotenv
import os
# load .env in case we're running via command line and don't have docker loading in env
load_dotenv("../.env")

# ASSEMBLYAI
def env_get_assembly_ai_api_key():
  return os.environ['ASSEMBLY_AI_API_KEY']

# AWS
def env_get_aws_access_key_id():
  return os.environ['AWS_ACCESS_KEY_ID']
def env_get_aws_secret_access_key():
  return os.environ['AWS_SECRET_ACCESS_KEY']
def env_get_aws_s3_files_bucket():
  return os.environ['AWS_S3_FILES_BUCKET']

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
def env_get_database_app_url():
  return f"postgresql+asyncpg://{env_get_database_app_user_name()}:{env_get_database_app_user_password()}@{env_get_database_app_host()}:{env_get_database_app_port()}/{env_get_database_app_name()}"
def env_get_database_pinecone_api_key():
  return os.environ['DATABASE_PINECONE_API_KEY']
def env_get_database_pinecone_environment():
  return os.environ['DATABASE_PINECONE_ENVIRONMENT']

# GIDEON
def env_get_gideon_api_url():
  return "http://localhost:3000"

# HARDWARE
def env_is_gpu_available():
  is_gpu_available = os.environ['IS_GPU_AVAILABLE'] == 'true'
  print(f'INFO (env.py:env_is_gpu_available): is_gpu_available : {is_gpu_available}')
  return is_gpu_available

# OPENAI
def env_get_open_ai_api_key():
  return os.environ['OPEN_AI_API_KEY']
