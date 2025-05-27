from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio

from database import init_db, add_order, get_order_by_id, publish_event
from models import Order

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    init_db()
    # If you need the outbox worker:
    # threading.Thread(target=outbox_worker, daemon=True).start()


@app.post('/orders')
async def create_order(order: Order):
    try:
        add_order(order.order_id, order.item)

        event = {'type': 'order_created', 'order_id': order.order_id, 'item': order.item}
        asyncio.create_task(publish_event(event))

        return {
            'status': 'order created',
            'order': order.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/orders/{order_id}')
async def get_order(order_id: str):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order with ID {order_id} not found"
        )
    return order


@app.get('/health')
def health_check():
    return {'status': 'healthy', "service": "payment_service"}


if __name__ == '__main__':
    # threading.Thread(target=outbox_worker, daemon=True).start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
