import json
import asyncio
import aiohttp
import aiohttp.web
import logging
import rethinkdb as r


r.set_loop_type("asyncio")
LOG = logging.getLogger(__name__)
DB_NAME = "smoothie"
TABLE_NAME = "plugins"


async def websocket_handler(request):
    """
        Handles wesockets, waits for a change in
        ``TABLE_NAME`` rethinkdb table
    """
    ws_ = aiohttp.web.WebSocketResponse()
    assert ws_.can_start(request)
    await ws_.prepare(request)

    conn = await r.connect()
    cursor = await r.db(DB_NAME).table(TABLE_NAME).changes().run(conn)
    while await cursor.fetch_next():
        ws_.send_str(json.dumps(await cursor.next()))

    return ws_


async def init(loop):
    """ init """
    app_ = aiohttp.web.Application(loop=loop)
    app_.router.add_route('GET', '/', websocket_handler)
    await loop.create_server(app_.make_handler(), '127.0.0.1', 9000)
    return app_


async def client():
    """ Client """
    session = aiohttp.ClientSession()
    async with session.ws_connect('http://localhost:9000/') as ws_:
        async for msg in ws_:
            LOG.info(msg)


def socketserver():
    """ Server """
    asyncio.get_event_loop().run_until_complete(client())


def socketclient():
    """ Client """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
