#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    TargetNetwork module

    Gets the target network selected by the client (in whatever format)
    standarizes it and adds extra data
"""

from smoothie.plugins import SmoothiePlugin


class TargetNetwork(SmoothiePlugin):
    """
        Updates target network (bssid) with extra data
    """
    timeout = 5 * 60  # 5 minutes is actually a HUGE timeout for this one

    def callback(self):
        """
            Creates target tree
        """

        def get_childrens(par):
            """
                Looks for childrens of a specific parent
            """
            clients = self.mongo_document['clients']
            if not clients:
                return []
            return [a for a in clients if a['ssid'] == par['bssid']]

        if not isinstance(self.mongo_document["target"], dict):
            for target_ in self.mongo_document['aps']:
                if target_['bssid'] == self.mongo_document["target"]:
                    target = target_
                    break
            else:
                return

        for tar in self.mongo_document['aps']:
            if tar['bssid'] == target['bssid']:
                parent = tar
                break
        else:
            return

        tree = [parent, get_childrens(parent)]
        self.update({'$set': {'target': target}})
        self.update({'$set': {'target_tree': tree}})
        self.stop()


def run():
    """ main """
    return str(TargetNetwork())
