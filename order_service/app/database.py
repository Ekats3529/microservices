import psycopg2
import psycopg2.extras
import asyncio
import aio_pika
import os
import json

conn = psycopg2.connect(
    database="orders",
    user="user",
    password="1234",
    host="postgres"
)

conn.autocommit = True
conn.set_client_encoding('UTF8')

db = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    db.execute("""
             CREATE TABLE IF NOT EXISTS orders (
                 id VARCHAR PRIMARY KEY,
                 item VARCHAR
             );
        """)
    db.execute("""
            CREATE TABLE IF NOT EXISTS outbox (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR NOT NULL,
                payload JSONB NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            );
        """)


def add_order(order_id, item):
    db.execute("INSERT INTO orders (id, item) VALUES (%s, %s)", (order_id, item))
    event = {
        "type": "order_created",
        "order_id": order_id,
        "item": item
    }
    db.execute(
        "INSERT INTO outbox (event_type, payload) VALUES (%s, %s)",
        ("order_created", json.dumps(event))
    )


def get_order_by_id(order_id):
    db.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = db.fetchone()
    if not order:
        return None
    return dict(order)


async def publish_event(event: dict):
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=str(event).encode()),
        routing_key="order_events"
    )
    await connection.close()


async def outbox_worker():
    print("[*] Outbox worker started")
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

    while True:
        try:
            db.execute("SELECT * FROM outbox WHERE processed = FALSE LIMIT 10")
            rows = db.fetchall()

            if not rows:
                await asyncio.sleep(2)
                continue

            connection = await aio_pika.connect_robust(rabbitmq_url)
            channel = await connection.channel()

            for row in rows:
                message = aio_pika.Message(body=json.dumps(row['payload']).encode())
                await channel.default_exchange.publish(message, routing_key="order_events")
                db.execute("UPDATE outbox SET processed = TRUE WHERE id = %s", (row['id'],))

            await connection.close()

        except Exception as e:
            print(f"[!] Outbox worker error: {e}")
            await asyncio.sleep(5)
