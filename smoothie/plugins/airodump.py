#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    List networks
"""

from smoothie.plugins import SmoothiePlugin
from pyrcrack.management import Airmon
from pyrcrack.scanning import Airodump
from contextlib import suppress
import time


class AirodumpPlugin(SmoothiePlugin):
    """
        Handle airmon and airodump using pyrcrack to set a target tree in mongo
    """
    def run(self):
        """
            Main loop
        """

        while 'wifi' not in self.mongo_document:
            time.sleep(10)

        with Airmon(self.mongo_document['wifi']) as mon:
            self.update({'$set': {'monitor': mon.interface}})
            kwargs = {}
            with suppress(KeyError):
                kwargs = self.mongo_document['plugin_data']['airodump']
            with Airodump(mon.interface, **kwargs) as air:
                while self.do_run:
                    time.sleep(10)
                    self.set({'tree': air.tree})

        self.teardown()


def airodump():
    """ main """
    return str(AirodumpPlugin())
