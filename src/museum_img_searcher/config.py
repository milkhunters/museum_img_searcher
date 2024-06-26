import os
from dataclasses import dataclass
from logging import getLogger

import yaml
import consul
from dotenv import load_dotenv

logger = getLogger(__name__)


class ConfigParseError(ValueError):
    pass


@dataclass
class PostgresConfig:
    DATABASE: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int = 5432


@dataclass
class RabbitMQ:
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    VHOST: str


@dataclass
class S3Config:
    BUCKET: str
    ENDPOINT_URL: str
    PUBLIC_ENDPOINT_URL: str
    REGION: str
    ACCESS_KEY_ID: str
    ACCESS_KEY: str


@dataclass
class Control:
    SEARCHER_TASKS_SENDER_ID: str
    SEARCHER_TASKS_RECEIVER_ID: str
    RABBITMQ: RabbitMQ


@dataclass
class Config:
    DEBUG: bool
    POSTGRESQL: PostgresConfig
    S3: S3Config
    CONTROL: Control


def to_bool(value) -> bool:
    return str(value).strip().lower() in ("yes", "true", "t", "1")


def get_str_env(key: str, optional: bool = False) -> str:
    val = os.getenv(key)
    if not val and not optional:
        logger.error("%s is not set", key)
        raise ConfigParseError(f"{key} is not set")
    return val


def load_config() -> Config:
    """
    Load config from consul

    """
    env_file = ".env"

    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        logger.info("Loading env from os.environ")

    is_debug = to_bool(get_str_env('DEBUG'))
    root_name = get_str_env("CONSUL_ROOT")
    host = get_str_env("CONSUL_HOST")
    port = int(get_str_env("CONSUL_PORT"))

    raw_yaml_config = consul.Consul(host=host, port=port, scheme="http").kv.get(root_name)[1]['Value'].decode("utf-8")
    if not raw_yaml_config:
        raise ConfigParseError("Consul config is empty")
    config = yaml.safe_load(raw_yaml_config)

    return Config(
        DEBUG=is_debug,
        POSTGRESQL=PostgresConfig(
            DATABASE=config['postgresql']['database'],
            USERNAME=config['postgresql']['username'],
            PASSWORD=config['postgresql']['password'],
            HOST=config['postgresql']['host'],
            PORT=config['postgresql'].get('port', 5432),
        ),
        CONTROL=Control(
            SEARCHER_TASKS_SENDER_ID=config['control']['searcher_tasks_sender_id'],
            SEARCHER_TASKS_RECEIVER_ID=config['control']['searcher_tasks_receiver_id'],
            RABBITMQ=RabbitMQ(
                HOST=config['control']['rabbitmq']['host'],
                PORT=config['control']['rabbitmq']['port'],
                USERNAME=config['control']['rabbitmq']['username'],
                PASSWORD=config['control']['rabbitmq']['password'],
                VHOST=config['control']['rabbitmq']['vhost']
            )
        ),
        S3=S3Config(
            ENDPOINT_URL=config['s3']['endpoint_url'],
            REGION=config['s3']['region'],
            ACCESS_KEY_ID=config['s3']['access_key'],
            ACCESS_KEY=config['s3']['secret_key'],
            BUCKET=config['s3']['bucket'],
            PUBLIC_ENDPOINT_URL=config['s3']['public_endpoint_url']
        ),
    )
