from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class LexicalUnit:
    lu_id: int
    lemma: str
    pos: int
    domain: int
    variant: int

    POS_STR_DICT = {
        1: "verb",
        2: "noun",
        3: "adverb",
        4: "adjective",
        5: "verb_en",
        6: "noun_en",
        7: "adverb_en",
        8: "adjective_en",
    }

    def __str__(self):
        pos = self.POS_STR_DICT[self.pos]
        return f"{self.lemma}:{pos}:{self.variant}"


@dataclass(frozen=True)
class Synset:
    synset_id: int
    lu_set: Set[LexicalUnit]

    def __str__(self):
        lus = set(map(str, self.lu_set))
        lus = ", ".join(lus)
        return f"{self.synset_id}: ({lus})"
