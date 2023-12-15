import json
from typing import Any

from aio_pika import connect, Message
from utils.config import get_settings


class RabbitQueue:
    def __init__(self, url: str):
        self.url = url
    
    async def connect(self):
        self.connection = await connect(self.url)

    async def send_rabbitmq(self, msg: Any, routing_key: str):
        self.channel = await self.connection.channel()

        await self.channel.default_exchange.publish(
            Message(json.dumps(msg.model_dump()).encode("utf-8")),
            routing_key = routing_key
        )
    
    async def declare_queue(self, queue: str):
        return await self.channel.declare_queue(queue)

    async def close(self):
        await self.connection.close()

# queue_rabbit = RabbitQueue(url = get_settings().rabit_url)
queue_rabbit = RabbitQueue(url = "amqp://guest:guest@rabbitmq/")
