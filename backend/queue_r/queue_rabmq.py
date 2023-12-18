import json
from typing import Any

from aio_pika import connect, Message, ExchangeType
from utils.config import get_settings


class RabbitQueue:
    connection = None
    channel = None
    exchange = None

    def __init__(self, url: str):
        self.url = url
    
    async def connect(self):
        self.connection = await connect(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

    async def send_rabbitmq(self, msg: Any, routing_key: str):
        await self.exchange.publish(
            Message(json.dumps(msg.model_dump()).encode("utf-8")),
            routing_key = routing_key
        )
    
    async def declare_queue(self, name: str):
        return await self.channel.declare_queue(name, exclusive=True, durable=True)

    async def declare_exchange(self, name: str, type: ExchangeType=ExchangeType.FANOUT):
        self.exchange = await self.channel.declare_exchange(name, type, durable=True)
        return self.exchange

    async def close(self):
        await self.connection.close()

# queue_rabbit = RabbitQueue(url = get_settings().rabit_url)
queue_rabbit = RabbitQueue(url = "amqp://guest:guest@rabbitmq/")
