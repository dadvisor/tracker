import unittest

from tracker import Database
from tracker.database.node import Node
from math import floor, ceil


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.database = Database()

    def test_get(self):
        key = 'abc'
        assert self.database._get(key) == []

    def test_add(self):
        key = 'abc'
        node = Node('ip', 'port', True)
        self.database.add(key, node)
        assert self.database._get(key) == [node]

    def test_add_unique(self):
        key = 'abc'
        node = Node('ip', 'port', True)
        node2 = Node('ip', 'port', True)
        self.database.add(key, node)
        self.database.add(key, node2)
        assert self.database._get(key) == [node]
        assert self.database._get(key) == [node2]

    def test_remove(self):
        key = 'abc'
        node = Node('ip', 'port', True)
        self.database.add(key, node)
        assert self.database._get(key) == [node]
        self.database.remove(key, Node('ip', 'port', True))
        assert self.database._get(key) == []

    def test_distribute(self):
        key = 'abc'
        n_super_nodes = 3
        n_nodes = 11
        avg = n_nodes / n_super_nodes
        bound = (floor(avg), ceil(avg))

        super_nodes = [Node(f'ip{i}', 'port', True) for i in range(n_super_nodes)]
        nodes = [Node('ip', f'port{i}', False) for i in range(n_nodes)]

        for node in super_nodes + nodes:
            self.database.add(key, node)

        distribution = self.database.distribute(key)

        for super_node, node_list in distribution:
            assert super_node in super_nodes
            assert bound[0] <= len(node_list) <= bound[1]
