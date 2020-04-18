from pathlib import Path
from typing import Dict, Set, Tuple

from plwn_graph_builder.database import get_engine
from plwn_graph_builder.vertices import LexicalUnit, Synset


class PLWN:

    def __init__(self, db_path: Path):
        self._db = get_engine(db_path)

    def lexical_units(self) -> Dict[int, LexicalUnit]:
        query = ('SELECT DISTINCT '
                 'id AS lu_id, lemma, pos, domain, variant '
                 'FROM lexicalunit;')

        results = self._db.execute(query)
        lexical_units = {
            row.lu_id: LexicalUnit(**row)
            for row in results
        }
        results.close()

        return lexical_units

    def synsets(self) -> Dict[int, Synset]:
        query = ('SELECT DISTINCT '
                 'id AS synset_id '
                 'FROM synset;')

        results = self._db.execute(query)
        synsets_indices = [
            row.synset_id
            for row in results
        ]
        synsets_lexical_units = [
            self.synset_lexical_units(synset_id=idx)
            for idx in synsets_indices
        ]
        synsets = {
            synset_id: lu_set
            for synset_id, lu_set in zip(synsets_indices, synsets_lexical_units)
        }
        results.close()

        return synsets

    def synset_lexical_units(self, synset_id: int) -> Set[LexicalUnit]:
        query = (f'SELECT DISTINCT '
                 f'lex_id AS lexical_unit_id '
                 f'FROM unitandsynset '
                 f'WHERE syn_id={synset_id};')

        results = self._db.execute(query)
        lexical_units = {
            row.lexical_unit_id
            for row in results
        }
        results.close()

        return lexical_units

    def synsets_relations(self) -> Set[Tuple[int, int, int]]:
        query = ('SELECT DISTINCT '
                 'parent_id, child_id, rel_id AS relation_id '
                 'FROM synsetrelation;')

        results = self._db.execute(query)

        relations = {
            (parent_id, child_id, relation_id)
            for parent_id, child_id, relation_id in results
        }
        results.close()

        return relations

    def lexical_units_relations(self) -> Set[Tuple[int, int, int]]:
        query = ('SELECT DISTINCT '
                 'parent_id, child_id, rel_id AS relation_id '
                 'FROM lexicalrelation;')

        results = self._db.execute(query)

        relations = {
            (parent_id, child_id, relation_id)
            for parent_id, child_id, relation_id in results
        }
        results.close()

        return relations
