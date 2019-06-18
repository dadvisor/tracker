import unittest

from tracker import Database
from tracker.model.node import Node
from math import floor, ceil


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.database = Database()

    def test_add(self):
        node = Node('ip', 123, True)
        self.database.add(node)
        assert self.database.node_list == [node]

    def test_add_unique(self):
        node = Node('ip', 124, True)
        node2 = Node('ip', 124, True)
        self.database.add(node)
        self.database.add(node2)
        assert self.database.node_list == [node]
        assert self.database.node_list == [node2]

    def test_remove(self):
        node = Node('ip', 125, True)
        self.database.add(node)
        assert self.database.node_list == [node]
        self.database.remove(Node('ip', 125, True))
        assert self.database.node_list == []

    def test_distribute(self):
        n_super_nodes = 3
        n_nodes = 11
        avg = n_nodes / n_super_nodes
        bound = floor(avg), ceil(avg)

        super_nodes = [Node(f'ip{i}', 126, True) for i in range(n_super_nodes)]
        nodes = [Node('ip', 100+i, False) for i in range(n_nodes)]

        for node in super_nodes + nodes:
            self.database.add(node)

        distribution = self.database.distribute()

        for super_node, node_list in distribution:
            assert bound[0] <= len(node_list) <= bound[1]
