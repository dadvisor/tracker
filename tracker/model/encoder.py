from json import JSONEncoder

from tracker.model import Node


class JSONCustomEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Node):
            return obj.__dict__()
        return JSONEncoder.default(self, obj)
