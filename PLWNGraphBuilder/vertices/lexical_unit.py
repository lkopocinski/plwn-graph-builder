from collections import OrderedDict


class LexicalUnit:

    POS_STR = [
        "verb", "noun", "adverb", "adjective",
        "verb_en", "noun_en", "adverb_en", "adjective_en",
    ]

    def __init__(self, lu_id, lemma, pos, domain, variant, lexicon=None):
        self.lu_id = lu_id
        self.lemma = lemma
        self.pos = pos
        self.domain = domain
        self.variant = variant
        self.lexicon = lexicon

    def _fields(self):
        fields = OrderedDict([
            ("lu_id", self.id),
            ("lemma", self._stringify(self.lemma)),
            ("pos", self.pos),
            ("domain", self.domain),
            ("variant", self.variant),
            ("lexicon", self._stringify(self.lexicon)),
        ])
        # We still have pickled graphs without comments for whatever reason
        try:
            fields["comment"] = self._stringify(self.comment)
        except AttributeError:
            pass
        return fields

    @staticmethod
    def _stringify(value):
        if value is None:
            return "None"
        return "'" + value.replace("'", "\\'") + "'"

    def __repr__(self):
        return "<{}({})>".format(type(self).__name__, ", ".join(
            "{}={}".format(k, v) for (k, v) in self._fields().items()))

    def __str__(self):
        pos = self.POS_STR[self.pos + 1]
        return "{}:{}:{}".format(self.lemma, pos, self.variant)
