import os
import aio_pika


async def consume():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()

    queue = await channel.declare_queue("payment_events", durable=True)

    print("[*] Notification service is listening for payment events...")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(f"[Notification] Payment confirmed: {message.body.decode()}")
