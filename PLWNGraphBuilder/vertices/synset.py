from collections import OrderedDict


class Synset:
    def __init__(self, synset_id, lu_set):
        self.synset_id = synset_id
        self.lu_set = lu_set

    def _fields(self):
        return OrderedDict([
            ("synset_id", self.synset_id),
            ("lu_set", self._stringify_set(self.lu_set)),
        ])

    @staticmethod
    def _stringify_set(units, method=repr):
        if units is None:
            return "None"
        return "'" + ", ".join(repr(unit) for unit in units) + "'"

    def __repr__(self):
        return "<{}({})>".format(type(self).__name__, ", ".join(
            "{}={}".format(k, v) for (k, v) in self._fields().items()))

    def __str__(self):
        return '{}: {}'.format(
            self.synset_id, self._stringify_set(self.lu_set, str))
