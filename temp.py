import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

# AWS_S3_SIGNATURE_VERSION = 's3v4'
# # AWS_S3_REGION_NAME = 'eu-west-2'
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = None
# AWS_S3_VERIFY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
#                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                                   config=Config(signature_version='s3v4'),)

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  )

def upload_file_to_s3(local_file_path, s3_filename):
    try:
        with open(local_file_path, 'rb') as file:
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, f'Inhouse/{s3_filename}')
        print(f"File {s3_filename} uploaded successfully to bucket {AWS_STORAGE_BUCKET_NAME}!")
    except FileNotFoundError:
        print(f"The file {local_file_path} was not found.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("Access Denied. Please check your AWS credentials and bucket permissions.")
        elif e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"The bucket {AWS_STORAGE_BUCKET_NAME} does not exist.")
        else:
            print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Usage example
# local_file_path = '/home/bacancy/Development/AutomedSEO/automated_seo/custom_addons/automated_seo/static/src/img/angular.svg'
# s3_filename = 'angular.svg'
#
# # Upload the file to S3
# # upload_file_to_s3(local_file_path, s3_filename)
# response = s3.list_buckets()
# buckets = [bucket['Name'] for bucket in response['Buckets']]
# print("Available buckets:", buckets)
#
# try:
#     response = s3.list_objects_v2(Bucket=AWS_STORAGE_BUCKET_NAME)
#     print("Bucket contents:", response.get('Contents', []))
# except ClientError as e:
#     print(f"Error listing bucket contents: {e}")
def list_s3_files(bucket_name, folder_name):
    s3 = boto3.client('s3')

    # Use the list_objects_v2 method to get the files
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    # Check if there are contents in the response
    if 'Contents' in response:
        print(f"Files in folder '{folder_name}':")
        for file in response['Contents']:
            print(file['Key'])  # 'Key' contains the file path/name
    else:
        print(f"No files found in folder '{folder_name}'.")


# Replace with your bucket and folder name
bucket_name =AWS_STORAGE_BUCKET_NAME
folder_name = 'Inhouse/'  # Note the trailing slash


local_file_path = '/home/bacancy/Development/AutomedSEO/automated_seo/custom_addons/automated_seo/static/src/img/australia-flag.svg'
s3_filename = 'australia-flag.svg'

# Upload the file to S3
# upload_file_to_s3(local_file_path, s3_filename)
list_s3_files(bucket_name, folder_name)
