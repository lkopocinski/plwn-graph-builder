import logging
from pathlib import Path
from typing import Dict, Set

from graph_tool import Graph, load_graph

from plwn_graph_builder.vertices import LexicalUnit, Synset

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)


class PLWNGraph:
    SYNSET_PROPERTY_KEY = 'synset'
    LEXICAL_UNIT_PROPERTY_KEY = 'lu'
    EDGE_PROPERTY_KEY = 'int'
    RELATION_PROPERTY_KEY = 'rel_id'

    def __init__(self):
        self._db = None

        self._synset_G = Graph()
        self.lexical_units_G = Graph()

        self._lexical_units_dict = None
        self._synsets_dict = None

        self._synset_to_vertex_dict = None
        self._lexical_unit_to_vertex_dict = None

    def load_syn_graph(self, syn_graph_file):
        self._synset_G = load_graph(syn_graph_file)

    def load_lu_graph(self, lu_graph_file):
        self.lexical_units_G = load_graph(lu_graph_file)

    def build_graphs(self, db_connection):
        self._db = db_connection

        self._lexical_units_dict = self._get_lexical_units()
        self._synsets_dict = self._get_synsets()

        self._add_synset_vertices()
        self._add_lexical_units_vertices()

        self._add_synset_edges()
        self._add_lexical_units_edges()

    def _get_lexical_units(self) -> Dict[int, LexicalUnit]:
        query = 'SELECT DISTINCT ' \
                'id AS lu_id, lemma, pos, domain, variant ' \
                'FROM lexicalunit;'

        results = self._db.execute(query)
        lexical_units = {
            row.lu_id: LexicalUnit(**row)
            for row in results
        }
        results.close()

        return lexical_units

    def _get_synsets(self) -> Dict[int, Synset]:
        query = 'SELECT DISTINCT ' \
                'id AS synset_id ' \
                'FROM synset;'

        results = self._db.execute(query)
        synsets_indices = [
            row.synset_id
            for row in results
        ]
        synsets_lexical_units = [
            self._get_synsets_lexical_units(index)
            for index in synsets_indices
        ]
        synsets = {
            index: lu_set
            for index, lu_set in zip(synsets_indices, synsets_lexical_units)
        }
        results.close()

        return synsets

    def _get_synsets_lexical_units(self, synset_id: int) -> Set[LexicalUnit]:
        query = f'SELECT DISTINCT ' \
                f'lex_id AS lu_id ' \
                f'FROM unitandsynset ' \
                f'WHERE syn_id={synset_id};'

        results = self._db.execute(query)
        lexical_units = {
            self._lexical_units_dict[row.lu_id]
            for row in results
            if row.lu_id in self._lexical_units_dict
        }
        results.close()

        return lexical_units

    def _add_synset_vertices(self) -> None:
        self._synset_to_vertex_dict = {}

        vertex_property = self._synset_G.new_vertex_property(
            'python::object'
        )
        for synset_id, synset in self._synsets_dict.items():
            vertex = self._synset_G.add_vertex()
            vertex_property[vertex] = synset
            self._synset_to_vertex_dict[synset_id] = vertex

        self._synset_G.vertex_properties[
            self.SYNSET_PROPERTY_KEY
        ] = vertex_property

    def _add_lexical_units_vertices(self) -> None:
        self._lexical_unit_to_vertex_dict = {}

        vertex_property = self.lexical_units_G.new_vertex_property(
            'python::object'
        )
        for lu_id, lu in self._lexical_units_dict.items():
            vertex = self.lexical_units_G.add_vertex()
            vertex_property[vertex] = lu
            self._lexical_unit_to_vertex_dict[lu_id] = vertex

        self.lexical_units_G.vertex_properties[
            self.LEXICAL_UNIT_PROPERTY_KEY
        ] = vertex_property

    def _add_synset_edges(self) -> None:
        edge_property_relation_id = self._synset_G.new_edge_property(
            self.EDGE_PROPERTY_KEY
        )

        query = 'SELECT DISTINCT ' \
                'parent_id, child_id, rel_id ' \
                'FROM synsetrelation;'

        results = self._db.execute(query)
        for row in results:
            parent_id, child_id, relation_id = row

            if parent_id in self._synset_to_vertex_dict:
                vertex_parent_id = self._synset_to_vertex_dict[parent_id]
            else:
                logger.warning(
                    f'Parent synset {parent_id} '
                    f'appears in synsetrelation table '
                    f'but is missing in synset table.'
                )
                continue

            if child_id in self._synset_to_vertex_dict:
                vertex_child_id = self._synset_to_vertex_dict[child_id]
            else:
                logger.warning(
                    f'Child sysnet {child_id} '
                    f'appears in synsetrelation table '
                    f'but is missing in synset table.',
                )
                continue

            edge = self._synset_G.add_edge(
                vertex_parent_id, vertex_child_id
            )
            edge_property_relation_id[edge] = relation_id

        self._synset_G.edge_properties[
            self.RELATION_PROPERTY_KEY
        ] = edge_property_relation_id

    def _add_lexical_units_edges(self):
        edge_property_relation_id = self.lexical_units_G.new_edge_property(
            self.EDGE_PROPERTY_KEY
        )

        query = 'SELECT DISTINCT ' \
                'parent_id, child_id, rel_id ' \
                'FROM lexicalrelation;'

        results = self._db.execute(query)
        for row in results:
            parent_id, child_id, relation_id = row

            if parent_id in self._lexical_unit_to_vertex_dict:
                vertex_parent_id = self._lexical_unit_to_vertex_dict[
                    parent_id
                ]
            else:
                logger.warning(
                    f'Parent lexical unit {parent_id} '
                    f'appears in synsetrelation table '
                    f'but is missing in unitandsynset table.',
                )
                continue

            if child_id in self._lexical_unit_to_vertex_dict:
                vertex_child_id = self._lexical_unit_to_vertex_dict[
                    child_id
                ]
            else:
                logger.warning(
                    f'Child lexical unit {child_id} '
                    f'appears in synsetrelation table '
                    f'but is missing in unitandsynset table.',
                )
                continue

            edge = self.lexical_units_G.add_edge(
                vertex_parent_id, vertex_child_id
            )
            edge_property_relation_id[edge] = relation_id

        self.lexical_units_G.edge_properties[
            self.RELATION_PROPERTY_KEY
        ] = edge_property_relation_id

    def save_graphs(self, out_dir: Path):
        synset_graph_path = out_dir / 'plwn_graph_syn.xml.gz'
        self._synset_G.save(synset_graph_path)

        lu_graph_path = out_dir / 'plwn_graph_lu.xml.gz'
        self.lexical_units_G.save(lu_graph_path)
