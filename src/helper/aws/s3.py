import boto3
import os
from botocore.exceptions import ClientError
from src.logger import Logger
from src.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, DEFAULT_BUCKET_NAME

log = Logger.get_logger()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = DEFAULT_BUCKET_NAME

    def upload_file(self, file, bucket_name: str, object_name: str):
        """Upload a file to S3"""
        try:
            self.s3_client.upload_fileobj(file, bucket_name, object_name)
            log.info(f"File uploaded successfully to s3://{bucket_name}/{object_name}")
            return True
        except ClientError as e:
            log.error(f"Error uploading file to S3: {e}")
            raise

    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """Download a file from S3"""
        try:
            self.s3_client.download_file(bucket_name, object_name, file_path)
            log.info(f"File downloaded successfully from s3://{bucket_name}/{object_name}")
            return True
        except ClientError as e:
            log.error(f"Error downloading file from S3: {e}")
            raise

    def generate_presigned_url(self, bucket_name: str, object_name: str, expiration: int = 3600):
        """Generate a presigned URL for S3 object"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            log.error(f"Error generating presigned URL: {e}")
            raise

    def check_object_existence(self, bucket_name: str, object_name: str):
        """Check if an object exists in S3"""
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def generate_valid_object_name(self, filename: str):
        """Generate a valid S3 object name from filename"""
        import uuid
        import re
        
        # Remove or replace invalid characters
        valid_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Add unique identifier to prevent conflicts
        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(valid_name)
        
        return f"{name}_{unique_id}{ext}"

def get_s3_service():
    """Dependency function to get S3 service"""
    return S3Service() 