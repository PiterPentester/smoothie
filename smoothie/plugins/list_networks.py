#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    List networks
"""

from smoothie.plugins import SmoothiePlugin
from pyrcrack.management import Airmon
from pyrcrack.scanning import Airodump
import time


class ListNetworks(SmoothiePlugin):
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
            with Airodump(mon.interface) as air:
                while self.do_run:
                    time.sleep(10)
                    self.set({'tree': air.tree})

        self.teardown()


def list_networks():
    """ main """
    return str(ListNetworks())
