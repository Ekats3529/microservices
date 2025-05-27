import psycopg2
import psycopg2.extras

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
    # db.execute("""
    #     CREATE TABLE IF NOT EXISTS orders (
    #         id VARCHAR PRIMARY KEY,
    #         item VARCHAR
    #     );
    #     CREATE TABLE IF NOT EXISTS outbox (
    #         id SERIAL PRIMARY KEY,
    #         event_type VARCHAR,
    #         payload JSONB,
    #         processed BOOLEAN DEFAULT FALSE
    #     );
    # """)
    db.execute("""
             CREATE TABLE IF NOT EXISTS orders (
                 id VARCHAR PRIMARY KEY,
                 item VARCHAR
             );
        """)


def add_order(order_id, item):
    db.execute("INSERT INTO orders (id, item) VALUES (%s, %s)", (order_id, item))
    # event = json.dumps({'type': 'order_created', 'order_id': order_id, 'item': item})
    # c.execute("INSERT INTO outbox (event) VALUES (?)", (event,))


def get_order_by_id(order_id):
    db.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = db.fetchone()
    if not order:
        return None
    return dict(order)
