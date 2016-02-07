#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    List networks
"""

from smoothie.plugins import GenericAircrackPlugin


class AirodumpPlugin(GenericAircrackPlugin):
    """
        Handle airmon and airodump using pyrcrack to set a target tree in mongo
    """
    _cls = "airodump"
    _module = "scanning"


def airodump():
    """ main """
    return str(AirodumpPlugin())
