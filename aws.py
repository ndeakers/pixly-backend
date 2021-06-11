import os
import boto3
from project_secrets import SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME

client = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)


def generate_aws_url(id):

    params = {
        'Bucket': f"{BUCKET_NAME}",
        'Key': f"{id}"}

    response = client.generate_presigned_url(
        'get_object',
        Params=params,
        ExpiresIn=100000)

    img_url = response.split("?")[0]
    return img_url
    # use library called urllib to parse urls


def upload_file(filename, id):
    client.upload_file(filename, BUCKET_NAME, f"{id}", ExtraArgs={"ACL":"public-read"})


def download_file(id, filename):
    client.download_file(f'{BUCKET_NAME}', f'{id}', filename)
