import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
from archiq_backend import settings

def generate_unique_filename(filename: str) -> str:
    unique_id = str(uuid.uuid4())
    extension = filename.split(".")[-1]
    return f"{unique_id}.{extension}"

class S3Client:
    def __init__(self):
        self.session = boto3.session.Session()
        self.s3_config = Config(
            signature_version='s3v4',
            s3={'payload_signing_enabled': False,}
        )
        self.s3_bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.s3_client = self.session.client(
            service_name='s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            config=self.s3_config,
        )

    def upload_to_s3(self, file_content: bytes, destination_blob_name: str):
        try:
            self.s3_client.put_object(Bucket=self.s3_bucket, Key=destination_blob_name, Body=file_content)
            print(f"File uploaded to {destination_blob_name}.")
        except NoCredentialsError:
            print("Credentials not available.")
            raise

    def download_from_s3(self, source_blob_name: str, destination_file_path: str):
        try:
            self.s3_client.download_file(Bucket=self.s3_bucket, Key=source_blob_name, Filename=destination_file_path)
            print(f"File {source_blob_name} downloaded to {destination_file_path}.")
        except FileNotFoundError as e:
            print(f"File {source_blob_name} not found.")
            print(e)
        except NoCredentialsError:
            print("Credentials not available.")
            raise

    def delete_from_s3(self, source_blob_name: str):
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=source_blob_name)
            print(f"File {source_blob_name} deleted.")
        except FileNotFoundError as e:
            print(f"File {source_blob_name} not found.")
            print(e)
        except NoCredentialsError:
            print("Credentials not available.")
            raise

