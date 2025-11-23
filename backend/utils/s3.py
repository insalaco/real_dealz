# backend/utils/s3.py
import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError, ClientError
import uuid

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

def upload_file_to_s3(file_bytes, filename, content_type=None):
    unique_filename = f"{uuid.uuid4()}_{filename}"
    try:
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=unique_filename,
            Body=file_bytes,
            ContentType=content_type or "application/octet-stream",
        )
        url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"
        return url
    except (NoCredentialsError, ClientError) as e:
        print("S3 upload failed:", e)
        return None
