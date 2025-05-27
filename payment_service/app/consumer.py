import os
import aio_pika


async def consume():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()

    queue = await channel.declare_queue("order_events", durable=True)

    async with queue.iterator() as queue_iter:
        print("[*] Waiting for messages in payment_service. To exit press CTRL+C")
        async for message in queue_iter:
            async with message.process():
                print(f"[x] Received message in payment_service: {message.body.decode()}")
