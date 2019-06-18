from tracker.model.node import Node


class Database(object):
    """
    The model consists of a list of Node-objects.
    """

    def __init__(self):
        self.node_list = []

    def add(self, item):
        if item not in self.node_list:
            self.node_list.append(item)
            return True
        return False

    def remove(self, item):
        if item in self.node_list:
            self.node_list.remove(item)
            return True
        return False

    def distribute(self):
        """
        Divides the nodes over the super nodes.
        :return: A list with tuples with (super_node, list of nodes)
        """
        nodes = [item for item in self.node_list if not item.is_super_node]
        super_nodes = [item for item in self.node_list if item.is_super_node]

        chunks = self.make_chunks(nodes, len(super_nodes))
        return [(super_nodes[i], node_list) for i, node_list in enumerate(chunks)]

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
