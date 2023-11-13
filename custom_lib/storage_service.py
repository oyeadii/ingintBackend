import boto3
from django.conf import settings
from botocore.exceptions import ClientError


class StorageService:
    def __init__(self):
        self.client = boto3.client('s3',
                                    aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                                    aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                                    region_name=settings.AWS_S3_REGION_NAME)
        
    def list_files(self, token, bucket_name):
        return self.client.list_objects_v2(Bucket=bucket_name, Prefix=token)['Contents']

    def get_file_content(self, identifier, bucket_name):
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=identifier)
            content_type = response['ContentType']
            return response['Body'].read(), content_type
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False, False
            else:
                raise Exception(f"An unexpected error occurred: {e}")

    def delete_file(self, identifier, bucket_name):
        return self.client.delete_object(Bucket=bucket_name, Key=identifier)
        
    def upload_file(self, file, path, bucket_name):
        self.client.upload_fileobj(
                                    file,
                                    bucket_name,
                                    path
                                )
        return "success"