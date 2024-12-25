# import filecmp
# import os

# import boto3
# from botocore.client import Config
# from django.conf import settings

# def get_client():
#     client = boto3.client(
#     "s3",
#     "us-east-2",
#     config=Config(signature_version='s3v4'),
#     aws_access_key_id='AKIA5CTMJR3CKQN7SHC7',
#     aws_secret_access_key='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',
# )
#     return client

# # AWS_ACCESS_KEY_ID = os.environ.get("engro_aws_access_key_id")
# # AWS_SECRET_ACCESS_KEY = os.environ.get("engro_aws_secret_access_key")

# s3_resource = boto3.resource(
#     "s3",
#     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
# )

# s3_client = boto3.client(
#     "s3",
#     settings.AWS_S3_REGION_NAME,
#     config=Config(signature_version='s3v4'),
#     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
# )



# def generate_presigned_url(key, expiry=60 * 60 * 24 * 7):
#     return s3_client.generate_presigned_url(
#         "put_object",
#         Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME,
#                 "Key": key,
#                 },
#         ExpiresIn=expiry,
#         HttpMethod="PUT"
#     )


# def generate_presigned_url_for_get(key, expiry=60 * 60 * 24 * 7, other_params=None):

#     if not other_params:
#         other_params = {}

#     return s3_client.generate_presigned_url(
#         "get_object",
#         Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME,
#                 "Key": key,
#                 **other_params
#                 },
#         ExpiresIn=expiry,
#         HttpMethod="GET"
#     )


# def upload_path_to_key(path, key):
#     s3_client.upload_file(str(path), settings.AWS_STORAGE_BUCKET_NAME, key)


# def get_key_metadata(key, raise_on_missing=False):
#     try:
#         resp = s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
#         return resp
#     except boto3.exceptions.botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             if raise_on_missing:
#                 raise e
#             else:
#                 return None
#         raise e


# def compare_path_to_key(path, key, by_size_only, known_path_size=None, raise_on_missing=False):
#     resp = get_key_metadata(key, raise_on_missing=raise_on_missing)
#     if not resp:
#         return False
#     local_size = known_path_size if known_path_size is not None else os.path.getsize(path)
#     remote_size = resp['ContentLength']
#     if local_size != remote_size:
#         return False
#     if by_size_only:
#         return True
#     tmp_path = '/tmp/scouting-s3-compare-path-tmp'  # TODO: Make configurable
#     s3_client.download_file(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Filename=tmp_path)
#     return filecmp.cmp(path, tmp_path, shallow=False)


# def copy(source_key, target_key, **kwargs):
#     return s3_client.copy_object(
#         Bucket=settings.AWS_STORAGE_BUCKET_NAME,
#         CopySource=f"{settings.AWS_STORAGE_BUCKET_NAME}/{source_key}",
#         Key=target_key,
#         **kwargs
#     )


# def delete(key):
#     return s3_client.delete_object(
#         Bucket=settings.AWS_STORAGE_BUCKET_NAME,
#         Key=key,
#     )

# def generate_presigned_url_for_get_SMC(key, bucket, expiry=60 * 60 * 24 * 7, other_params=None):
#     if not other_params:
#         other_params = {}
#     return s3_client.generate_presigned_url(
#         "get_object",
#         Params={"Bucket": bucket,
#                 "Key": key,
#                 **other_params
#                 },
#         ExpiresIn=expiry,
#         HttpMethod="GET"
#     )
