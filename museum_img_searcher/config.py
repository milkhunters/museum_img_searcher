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
class Control:
    SEARCHER_TASKS_SENDER_ID: str
    SEARCHER_TASKS_RECEIVER_ID: str
    RABBITMQ: RabbitMQ



@dataclass
class Config:
    DEBUG: bool
    POSTGRESQL: PostgresConfig
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
            DATABASE=config['POSTGRESQL']['DATABASE'],
            USERNAME=config['POSTGRESQL']['USERNAME'],
            PASSWORD=config['POSTGRESQL']['PASSWORD'],
            HOST=config['POSTGRESQL']['HOST'],
            PORT=config['POSTGRESQL'].get('PORT', 5432),
        ),
        CONTROL=Control(
            SEARCHER_TASKS_SENDER_ID=config['CONTROL']['SEARCHER_TASKS_SENDER_ID'],
            SEARCHER_TASKS_RECEIVER_ID=config['CONTROL']['SEARCHER_TASKS_RECEIVER_ID'],
            RABBITMQ=RabbitMQ(
                HOST=config['CONTROL']['RABBITMQ']['HOST'],
                PORT=config['CONTROL']['RABBITMQ']['PORT'],
                USERNAME=config['CONTROL']['RABBITMQ']['USERNAME'],
                PASSWORD=config['CONTROL']['RABBITMQ']['PASSWORD'],
                VHOST=config['CONTROL']['RABBITMQ']['VHOST']
            )
        )
    )
