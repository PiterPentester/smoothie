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
        List networks.
        This plugin:
            - Puts the selected network interface in monitor mode
            - Retrieves the monitor interface
            - Starts an analysis with airodump-ng in channel hoping
              mode
            - Teardown clears interface and kills airodump
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
                    self.update({'$set': {'tree': air.tree}})

        self.teardown()


def run():
    """ main """
    return str(ListNetworks())
