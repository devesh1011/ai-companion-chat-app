# receives the message from chat.ai.msg
# --> callback method task
# saves the message to redis, db
# sent back the message to ws endpoint
import aio_pika
import asyncio
from save_message import save_msg_to_db, store_msg_in_redis, publish_to_session_channel
import json
from config import get_settings


settings = get_settings()


async def main():
    connection = await aio_pika.connect_robust(
        url=f"amqp://guest:guest@{settings.RABBITMQ_HOST}/",
        client_properties={"connection_name": "message-dispatcher"},
    )

    channel = await connection.channel()

    queue = await channel.declare_queue("chat.ai.msg", durable=True)
    exchange = await channel.declare_exchange("chat_app", type="topic", durable=True)
    await queue.bind(exchange=exchange, routing_key="chat.ai.msg")
    print("Connected to RabbitMQ and bound queue", flush=True)

    async def callback(msg: aio_pika.abc.AbstractIncomingMessage):
        async with msg.process():
            try:
                message_data = json.loads(msg.body)
                print(f"Received AI response: {message_data}", flush=True)
                await save_msg_to_db(message_data)
                await store_msg_in_redis(message_data)
                await publish_to_session_channel(message_data)
            except Exception as e:
                print(f"Error processing message: {e}", flush=True)
                raise

    await queue.consume(callback=callback)
    print("Consumer started, waiting for messages...", flush=True)

    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
