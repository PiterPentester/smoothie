"""
    Smoothie
"""
import os
import json
import asyncio
import aiohttp
import importlib
import aiohttp.web
import jinja2
import aiohttp_jinja2
import rethinkdb as r
from smoothie.config import DB_NAME, TABLE_NAME, LOG

r.set_loop_type("asyncio")
CURR = os.path.dirname(__file__)


async def execute_plugin(**kwargs):
    """
        Runs a plugin
    """
    plugin = getattr(importlib.import_module("smoothie.plugins"),
                     kwargs['plugin'])

    async with plugin(**kwargs) as plugin:
        plugin.run_forever()


async def websocket_handler(request):
    """
        Handles wesockets, waits for a change in
        ``TABLE_NAME`` rethinkdb table
    """
    ws_ = aiohttp.web.WebSocketResponse()
    assert ws_.can_start(request)
    await ws_.prepare(request)

    conn = await r.connect()
    cursor = await r.db(DB_NAME).table(TABLE_NAME).changes(
        initial_changes=True).run(conn)
    while await cursor.fetch_next():
        ws_.send_str(json.dumps(await cursor.next()))

    return ws_


class Task(aiohttp.web.View):
    @aiohttp_jinja2.template('task.jinja2')
    async def get(self):
        return {'task_id': self.request.GET['task_id']}

    async def post(self):
        """ Create a task. """
        conn = await r.connect()
        await r.db(DB_NAME).table(TABLE_NAME).insert(
            await self.request.post()).run(conn)
        return aiohttp.web.Response(body='{}')


async def init(loop):
    """ init """

    @aiohttp_jinja2.template('index.jinja2')
    def main_handler(request):
        """ Main page """
        return {}

    app_ = aiohttp.web.Application(loop=loop)
    aiohttp_jinja2.setup(app_, loader=jinja2.FileSystemLoader(
        os.path.join(CURR, './templates/')))
    app_.router.add_route('*', '/task', Task)
    app_.router.add_route('GET', '/ws', websocket_handler)
    app_.router.add_route('GET', '/', main_handler)
    await loop.create_server(app_.make_handler(), '127.0.0.1', 9000)
    return app_


def socketserver():
    """ Server """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
