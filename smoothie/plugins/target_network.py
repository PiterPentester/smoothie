#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smoothie.plugins.base import SmoothiePlugin
import pydot
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

    def get_target_tree(self, target):
        """
            Gets target tree.
            It starts with the parent, not caring if the target
            is the client or the parent
        """
        def get_childrens(par):
            """
                Looks for childrens of a specific parent
            """
            clients = self.mongo_document['clients']
            if not clients:
                return []
            return [a for a in clients if a['ssid'] == par['bssid']]

        def get_parent(child):
            """
                Looks for the parent of a specific children
            """
            for tar in self.mongo_document['aps']:
                if tar['bssid'] == child['bssid']:
                    return tar

        parent = get_parent(target)

        return [parent, [a for a in get_childrens(parent)]]

    def get_target(self):
        """
            Returns the target identified by given bssid.
            TODO: Right now this only handles ap targets.
        """
        if not isinstance(self.target, dict):
            for target in self.mongo_document['aps']:
                if target['bssid'] == self.target:
                    return target
        raise Exception("Target not found. Review this.")

    def callback(self):
        """
            Creates target tree
        """

        def get_target_tree_jpg(tree):
            """
                Returns a dot diagram in jpg format of the network
            """

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
                    yield '"{}" -> "{}"'.format(tree[0]['bssid'],
                                                client['bssid'])
                yield "}"

            dialog = '\n'.join([a for a in do_tree()])
            gof = pydot.graph_from_dot_data(dialog)
            enc = base64.b64encode(gof.create(format='jpe'))
            return "data:image/jpg;base64,{}".format(enc)

        target = self.get_target()
        tree = self.get_target_tree(target)
        self.update({'$set': {'target': target}})
        self.update({'$set': {'target_tree': tree}})
        self.update({'$set': {'target_tree_jpg':
                              self.get_target_tree_jpg(tree)}})
        self.stop()


def run():
    """ main """
    return str(TargetNetwork())
