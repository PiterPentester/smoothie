#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    List networks
"""

from smoothie.plugins import SmoothiePlugin
import pyrcrack


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

    def callback(self):
        """
            - Put the selected network on monitor mode
            - Scan for networks
            - Add networks and clients into target array.
        """
        if 'wifi' not in self.mongo_document:
            return  # Wait for the user to choose a wifi.

        # Get monitor interface
        with pyrcrack.Airmon(self.mongo_document['wifi']) as mon:
            self.update({'$set': {'monitor': mon.moniface}})
            with pyrcrack.Airodump(mon.moniface) as air:
                for result in air.results:
                    self.update({'$set': result})


def run():
    """ main """
    return str(ListNetworks())
