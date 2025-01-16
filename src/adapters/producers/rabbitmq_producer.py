import json
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any

import aio_pika

logger = logging.getLogger(__name__)


class Producer(ABC):
    @abstractmethod
    async def publish(self, message):
        raise NotImplementedError

    @abstractmethod
    async def connect(self):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class RabbitMQProducer(Producer):
    def __init__(self, rabbitmq_url: str, queue_name: str):
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
            logger.info(f"Connected to RabbitMQ and declared queue '{self.queue_name}'")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise e

    async def publish(self, message: dict[str, Any]):
        if not self.channel:
            raise ConnectionError("RabbitMQ channel is not initialized")
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=self.queue_name
        )
        logger.info(f"Published message to queue '{self.queue_name}': {message}")

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
