
import json
import time
from enum import StrEnum

import boto3
import pika
from botocore.client import BaseClient as S3Client

from museum_img_searcher.config import load_config
from museum_img_searcher.searcher import search
from museum_img_searcher.adder import add
from utils.s3 import download_file


class Command(StrEnum):
    SEARCH = "search"
    ADD = "add"


def callback(route_key: str, s3_client: S3Client, bucket: str):
    def wrap(ch, method, properties, body: str):
        start_time = time.time()

        data = json.loads(body)
        file_id = data["file_id"]

        file = download_file(s3_client, bucket, f"searcher/{file_id}")

        if data["command"] == Command.ADD:
            print(f" [x] Received add task for file_id: {file_id}")
            exhibit_id = data["exhibit_id"]

            add(file, exhibit_id)
            print(f" [x] Add took {time.time() - start_time} seconds")
        elif data["command"] == Command.SEARCH:
            print(f" [x] Received search task for file_id: {file_id}")
            task_id = data["task_id"]
            result = search(file)
            print(f" [x] Search took {time.time() - start_time} seconds")

            ch.basic_publish(
                exchange="",
                routing_key=route_key,
                body=json.dumps({
                    "task_id": task_id,
                    "result": result
                }),
            )
        else:
            print(f" [x] Received unknown command: {data['command']}")

        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    return wrap


def main():
    config = load_config()

    rmq_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.CONTROL.RABBITMQ.HOST,
            port=config.CONTROL.RABBITMQ.PORT,
            virtual_host=config.CONTROL.RABBITMQ.VHOST,
            credentials=pika.PlainCredentials(
                config.CONTROL.RABBITMQ.USERNAME,
                config.CONTROL.RABBITMQ.PASSWORD
            )
        )
    )
    channel = rmq_connection.channel()

    channel.queue_declare(
        queue=config.CONTROL.SEARCHER_TASKS_SENDER_ID,
        durable=True,
        exclusive=False,
        auto_delete=False
    )

    channel.queue_declare(
        queue=config.CONTROL.SEARCHER_TASKS_RECEIVER_ID,
        durable=True,
        exclusive=False,
        auto_delete=False
    )

    s3_session = boto3.Session(
        aws_access_key_id=config.S3.ACCESS_KEY_ID,
        aws_secret_access_key=config.S3.ACCESS_KEY,
        region_name=config.S3.REGION,
    )

    s3_client = s3_session.client(
        "s3",
        endpoint_url=config.S3.ENDPOINT_URL,
        use_ssl=False,
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")

    channel.basic_consume(
        queue=config.CONTROL.SEARCHER_TASKS_RECEIVER_ID,
        on_message_callback=callback(
            config.CONTROL.SEARCHER_TASKS_SENDER_ID,
            s3_client,
            config.S3.BUCKET
        ),
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
