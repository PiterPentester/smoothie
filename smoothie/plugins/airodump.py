#!/usr/bin/env python3
"""
    Airodump Rethink interface
"""
from pyrcrack.scanning import Airodump
from . import RDBPlugin


class AirodumpRD(RDBPlugin):
    """
        Aidorump-ng plugin
    """
    @property
    def obj(self):
        """ Get object """
        return Airodump

    @property
    def value(self):
        """ Get value """
        return self._obj.tree
