import io

from botocore.client import BaseClient as S3Client


def download_file(client: S3Client, bucket: str, key: str) -> io.BytesIO:
    response = client.get_object(Bucket=bucket, Key=key)
    file_stream = io.BytesIO()
    file_stream.write(response['Body'].read())
    file_stream.seek(0)
    return file_stream
