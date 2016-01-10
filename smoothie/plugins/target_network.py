#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smoothie.plugins.base import SmoothiePlugin
import time


class TargetNetwork(SmoothiePlugin):
    """
        Updates target network (bssid) with extra data
    """
    timeout = 5 * 60  # 5 minutes is actually a HUGE timeout for this one

    @property
    def target(self):
        """
            Just the target
        """
        return self.mongo_document['target']

    def get_target_svg(self):
        """
            Returns a svg with current network associated with the target
        """
        tree = self.get_target_tree()
        return "TODO: Make this return an actual svg ='D"

    def get_target_tree(self):
        """
            Gets target tree.
            It starts with the parent, not caring if the target
            is the client or the parent
        """
        def get_childrens(par):
            """
                Looks for childrens of a specific parent
            """
            for tar in self.mongo_document['targets']:
                if tar['type'] == 'children' and tar['ssid'] == par['bssid']:
                    yield tar

        def get_parent(child):
            """
                Looks for the parent of a specific children
            """
            for tar in self.mongo_document['targets']:
                if tar['bssid'] == child['ssid']:
                    return tar

        if self.target.type == "client":
            parent = get_parent(self.target)
        else:
            parent = self.target

        return [parent, [a for a in get_childrens(parent)]]

    def get_target(self):
        """
            Returns the target identified by given bssid.
            It does not really care if it's a client or an AP.
        """
        if isinstance(self.target, dict):
            for target in self.mongo_document['targets']:
                if target['bssid'] == self.target:
                    return target

    def callback(self):
        """
            Waits until user has selected a target.
        """
        if 'target' not in self.mongo_document:
            time.sleep(10)
        self.update({'$set': {'target': self.get_target()}})
        self.update({'$set': {'target_svg': self.get_target_svg()}})
