#!/usr/bin/env python3
"""
    Plugin base class
"""
class RDBPlugin:
    """
        TODO: Document this.
    """
    _obj = False
    table = False
    conn = False

    def __init__(self, **kwargs):
        self.sid = kwargs.pop('session_id')
        self.plugin = kwargs.pop('plugin')
        self.filter = {'plugin': self.plugin, "session_id": self.sid}
        self.kwargs = kwargs

    @property
    def obj(self):
        """ Get object """
        raise NotImplementedError

    @property
    def value(self):
        """ Get value """
        raise NotImplementedError

    async def update(self):
        """ Puts current airodump tree in rethinkdb """
        LOG.debug("Updating value")
        return await self.table.filter(self.filter).update({
            'value': self.value, 'status': 'running'})

    async def run_forever(self):
        """ Run forever updating elements. """
        while True:
            await asyncio.sleep(5)
            await self.update()

    async def __aenter__(self):
        self._obj = self.obj(**self.kwargs)
        self.table = r.db(DB_NAME).table(TABLE_NAME)
        self.conn = await r.connect()
        self.table.insert({'plugin': self.plugin, 'session_id': self.sid})
        LOG.debug("Initialized cm")

    async def __aexit__(self, exc_type, exc_value, traceback):
        res = {'value': self.value, 'status': 'stopped'}
        if exc_type:
            res.update({'exception': exc_value})
        await self.table.filter(self.filter).update(res)
        return self._obj.stop()


