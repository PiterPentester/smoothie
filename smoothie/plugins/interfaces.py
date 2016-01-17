#!/usr/bin/env python

from wireless import Wireless
from smoothie.plugins import SmoothiePlugin


class Interfaces(SmoothiePlugin):
    """
        Updates in mongodb the interfaces list.
    """

    timeout = 2 * 60

    def callback(self):
        if 'wifi_list' not in self.mongo_document:
            def blacklisted(iface):
                """ Checks if interface starts with smoothie or mon """
                return iface.startswith('smoothie') or iface.startswith('mon')

            ifaces = [a for a in Wireless().interfaces()
                      if not blacklisted(a)]
            self.update({'$set': {'wifi_list': ifaces}})
            self.stop()


def run():
    """ main """
    return str(Interfaces())
