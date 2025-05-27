import os
import aio_pika
import json
import ast


async def consume():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()

    order_queue = await channel.declare_queue("order_events", durable=True)

    print("[*] Payment service is listening for order events...")

    async with order_queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                message_body = message.body.decode()
                try:
                    order = json.loads(message_body)
                except json.JSONDecodeError:
                    order = ast.literal_eval(message_body)

                print(f"[Payment] Processing payment for order: {order}")

                await channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps({
                        "status": "paid",
                        "order_id": order["order_id"]
                    }).encode()),
                    routing_key="payment_events"
                )
