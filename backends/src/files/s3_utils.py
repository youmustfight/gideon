import boto3
import io
from env import env_get_aws_access_key_id, env_get_aws_secret_access_key, env_get_aws_s3_files_bucket

s3 = boto3.client('s3',
    aws_access_key_id=env_get_aws_access_key_id(),
    aws_secret_access_key= env_get_aws_secret_access_key())

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_fileobj
def s3_upload_file(file_key, file):
    bucket = env_get_aws_s3_files_bucket()
    print(f"[s3_upload_file] upload start: '{bucket}/{file_key}'")
    s3.upload_fileobj(io.BytesIO(file.body), bucket, file_key)
    print(f"[s3_upload_file] upload finish: '{bucket}/{file_key}'")

def s3_upload_file_bytes(file_key, bytesio):
    bucket = env_get_aws_s3_files_bucket()
    print(f"[s3_upload_file_bytes] upload start: '{bucket}/{file_key}'")
    s3.upload_fileobj(bytesio, bucket, file_key)
    print(f"[s3_upload_file_bytes] upload finish: '{bucket}/{file_key}'")

def s3_upload_file_string(file_key, string):
    bucket = env_get_aws_s3_files_bucket()
    print(f"[s3_upload_file_string] upload start: '{bucket}/{file_key}'")
    s3.put_object(Body=string, Bucket=bucket, Key=file_key)
    print(f"[s3_upload_file_string] upload finish: '{bucket}/{file_key}'")

def s3_get_file_url(file_key):
    bucket = env_get_aws_s3_files_bucket()
    return f"https://s3.amazonaws.com/{bucket}/{file_key}"

def s3_get_file_bytes(file_key):
    bucket = env_get_aws_s3_files_bucket()
    byte_array = io.BytesIO()
    s3.download_fileobj(Bucket=bucket, Key=file_key, Fileobj=byte_array)
    print(f"[s3_get_file_bytes] downloaded '{bucket}/{file_key}'")
    # returns a python File obj, not our model
    return byte_array.getvalue()