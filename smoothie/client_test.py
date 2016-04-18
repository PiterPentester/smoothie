import aiohttp
import asyncio


async def client():
    """ Client """
    session = aiohttp.ClientSession()
    async with session.ws_connect('http://localhost:9000/') as ws_:
        async for msg in ws_:
            print(msg)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(client())
