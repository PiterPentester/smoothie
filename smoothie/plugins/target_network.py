#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smoothie.plugins.base import SmoothiePlugin
from pydot_modern import pydot
import base64


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

    def get_target_tree_jpg(self, tree):

        def diagize(elem):
            """
                Returns labeled element for dot.
            """
            vals = '\\n'.join(elem.values())
            return '"{}" [label="{}"]'.format(elem['bssid'], vals)

        def do_tree():
            """
                Returns a dot three (generator, each line).
            """
            yield "digraph G {"
            yield diagize(tree[0])

            for client in tree[1]:
                yield diagize(client)
                yield '"{}" -> "{}"'.format(tree[0]['bssid'], client['bssid'])
            yield "}"

        dialog = '\n'.join([a for a in do_tree()])
        g = pydot.graph_from_dot_data(dialog)
        enc = base64.b64encode(g.create(format='jpe'))
        return "data:image/jpg;base64,{}".format(enc)

    def callback(self):
        """
            Creates target tree
        """
        tree = self.get_target_tree()
        self.update({'$set': {'target': self.get_target()}})
        self.update({'$set': {'target_tree': tree}})
        self.update({'$set': {'target_tree_jpg':
                              self.get_target_tree_jpg(tree)}})
