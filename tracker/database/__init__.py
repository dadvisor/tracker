from typing import List

from tracker.database.node import Node


class Database(object):
    """
    The database consists of a dictionary.
    The key of this dictionary is a string. The value is a list of Node-objects.
    """

    def __init__(self):
        self.peer_dict = {}  # dict of lists

    def _get(self, key) -> List[Node]:
        if key not in self.peer_dict:
            self.peer_dict[key] = []
        return self.peer_dict[key]

    def add(self, key, node):
        items = self._get(key)
        if node not in items:
            items.append(node)
            return True
        return False

    def remove(self, key, node):
        items = self._get(key)
        if node in items:
            items.remove(node)
            return True
        return False

    def distribute(self, key):
        """
        Divides the nodes over the super nodes.
        :param key: the key for the super nodes.
        :return: A list with tuples with (super_node, list of nodes)
        """
        all_nodes = self._get(key)
        nodes = [node for node in all_nodes if not node.is_super_node]
        super_nodes = [node for node in all_nodes if node.is_super_node]

        chunks = self.make_chunks(nodes, len(super_nodes))
        return [(super_nodes[i].to_json(), [n.to_json() for n in node_list])
                for i, node_list in enumerate(chunks)]

    @staticmethod
    def make_chunks(seq, num):
        if num == 0:
            return []
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out
