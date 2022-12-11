import boto3
import json
import os

def _env_getter(secret_key):
    # HACK: whatever code is requesting envs, ensure we've fetched+set environ
    # HACK: idk if there's going to be something broken with this
    if (os.environ.get(secret_key) == None):
        set_secrets_on_env()
    return os.environ.get(secret_key)

# ASSEMBLYAI
def env_get_assembly_ai_api_key():
    return _env_getter('ASSEMBLY_AI_API_KEY')

# AUTH
def env_jwt_secret():
    return _env_getter('AUTH_JWT_SECRET')

# AWS
def env_get_aws_access_key_id():
    return _env_getter('AWS_ACCESS_KEY_ID')
def env_get_aws_secret_access_key():
    return _env_getter('AWS_SECRET_ACCESS_KEY')
def env_get_aws_s3_files_bucket():
    return _env_getter('AWS_S3_FILES_BUCKET')

# CAP
def env_get_caselaw_access_project():
    return _env_getter('CASELAW_ACCESS_PROJECT_API_KEY')

# DATABASE
def env_get_database_app_user_name():
    return _env_getter('DATABASE_APP_USER_NAME')
def env_get_database_app_user_password():
    return _env_getter('DATABASE_APP_USER_PASSWORD')
def env_get_database_app_name():
    return _env_getter('DATABASE_APP_NAME')
def env_get_database_app_host():
    return _env_getter('DATABASE_APP_HOST')
def env_get_database_app_port():
    return _env_getter('DATABASE_APP_PORT')
def env_get_database_app_url(driver="asyncpg"):
    return f"postgresql+{driver}://{env_get_database_app_user_name()}:{env_get_database_app_user_password()}@{env_get_database_app_host()}:{env_get_database_app_port()}/{env_get_database_app_name()}"
def env_get_database_pinecone_api_key():
    return _env_getter('DATABASE_PINECONE_API_KEY')
def env_get_database_pinecone_environment():
    return _env_getter('DATABASE_PINECONE_ENVIRONMENT')

# ENV
def env_target_service() -> str: # 'api' or 'worker'
    return _env_getter('TARGET_SERVICE')
def env_is_local() -> bool:
    return _env_getter('TARGET_ENV') == 'local'
def env_is_production() -> bool:
    return _env_getter('TARGET_ENV') == 'production'

# GIDEON
def env_get_gideon_api_url():
    return _env_getter('GIDEON_API_URL')
def env_get_gideon_api_host() -> str:
    return _env_getter('GIDEON_API_HOST')
def env_get_gideon_api_port() -> int:
    return int(_env_getter('GIDEON_API_PORT'))

# HARDWARE/SYSTEM
def env_is_gpu_available() -> bool:
    is_gpu_available = _env_getter('IS_GPU_AVAILABLE') == 'true'
    print(f'INFO (env.py:env_is_gpu_available): is_gpu_available : {is_gpu_available}')
    return is_gpu_available

# OPENAI
def env_get_open_ai_api_key():
    return _env_getter('OPEN_AI_API_KEY')

# QUEUE
def env_queue_rq_host():
    return _env_getter('QUEUE_RQ_HOST')
def env_queue_rq_port():
    return _env_getter('QUEUE_RQ_PORT')

# INITIALIZE (V2)
def set_secrets_on_env():
    session = boto3.session.Session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    client = session.client(service_name='secretsmanager', region_name=os.environ.get('AWS_REGION'))
    try:
        get_secret_value_response = client.get_secret_value(SecretId=os.environ.get('TARGET_ENV'))
        # Decrypts secret using the associated KMS key.
        secret = json.loads(get_secret_value_response['SecretString'])
        for key in dict(secret).keys():
            os.environ[key] = secret[key]
    except Exception as err:
        # For a list of exceptions thrown, see https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise err
