#!/usr/bin/env python3
"""
    Airodump Rethink interface
"""
import asyncio
from pyrcrack.scanning import Airodump
import rethinkdb as r
from smoothie.config import DB_NAME, LOG

r.set_loop_type("asyncio")
TABLE_NAME = "airodump"


class AirodumpRD:
    """
        This is an async context manager,
        the api is compatible with ``pyrcrack.Airodump``
        but adds a method ``update`` that gathers
        the current Airodump tree and updates it into
        rethinkdb.

        You need to specify a session_id as keyword argument
        that won't be passed to Airodump.

        Normal use would be::
            async with AirodumpRD(**aircrack_args, sesion_id="foo") as airo:
                await airo.run_forever()

    """
    air = False
    table = False
    conn = False

    def __init__(self, **kwargs):
        self.sid = kwargs.pop('session_id')
        self.filter = {"session_id": self.sid}
        self.kwargs = kwargs

    async def update(self):
        """ Puts current airodump tree in rethinkdb """
        LOG.debug("Updating tree")
        return await self.table.filter(self.filter).update({
            'value': self.air.tree, 'status': 'running'})

    async def run_forever(self):
        """ Run forever updating elements. """
        while True:
            await asyncio.sleep(5)
            await self.update()

    async def __aenter__(self):
        self.air = Airodump(**self.kwargs)
        self.table = r.db(DB_NAME).table(TABLE_NAME)
        self.conn = await r.connect()
        self.table.insert({'session_id': self.sid})
        LOG.debug("Initialized cm")

    async def __aexit__(self, exc_type, exc_value, traceback):
        res = {'value': self.air.tree, 'status': 'stopped'}
        if exc_type:
            res.update({'exception': exc_value})
        await self.table.filter(self.filter).update(res)
        return self.air.stop()


async def run_standalone(**kwargs):
    """ We need this to make it run from the job queue handler """
    async with AirodumpRD(**kwargs) as airo:
        await airo.run_forever()
