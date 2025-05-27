import asyncio
from consumer import consume

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())