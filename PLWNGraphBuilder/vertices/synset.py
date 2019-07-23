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
    def _stringify_set(units):
        return f"'{', '.join(repr(unit) for unit in units)}'" if units else "None"

    def __repr__(self):
        return "<{}({})>".format(type(self).__name__, ", ".join(
            "{}={}".format(k, v) for (k, v) in list(self._fields().items())))

    def __str__(self):
        return f'{self.synset_id}: {self._stringify_set(self.lu_set, str)}'
