# backend/utils/s3.py
import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError, ClientError
import uuid

def upload_file_to_s3(file_bytes, filename, content_type=None):
    """
    Uploads a file to S3 and returns the public URL.
    """
    unique_filename = f"{uuid.uuid4()}_{filename}"

    try:
        # Create S3 client inside the function
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

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
