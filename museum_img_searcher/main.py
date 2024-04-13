
import json
import time
from enum import StrEnum

import pika

from museum_img_searcher.config import load_config
from museum_img_searcher.searcher import search
from museum_img_searcher.adder import add


class Command(StrEnum):
    SEARCH = "search"
    ADD = "add"


def callback(route_key):
    def wrap(ch, method, properties, body: str):
        start_time = time.time()

        data = json.loads(body)
        file_id = data["file_id"]

        if data["command"] == Command.ADD:
            print(f" [x] Received add task for file_id: {file_id}")
            add(file_id)
            print(f" [x] Add took {time.time() - start_time} seconds")
        elif data["command"] == Command.SEARCH:
            print(f" [x] Received search task for file_id: {file_id}")
            task_id = data["task_id"]
            result = search(body)
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

    connection = pika.BlockingConnection(
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
    channel = connection.channel()

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

    print(" [*] Waiting for messages. To exit press CTRL+C")

    channel.basic_consume(
        queue=config.CONTROL.SEARCHER_TASKS_RECEIVER_ID,
        on_message_callback=callback(config.CONTROL.SEARCHER_TASKS_SENDER_ID)
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
