import io

from botocore.client import BaseClient as S3Client


def download_file(client: S3Client, bucket: str, key: str) -> io.BytesIO:
    obj = client.Object(bucket, key)
    data = io.BytesIO()
    obj.download_fileobj(data)
    return data


