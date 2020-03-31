import logging
import sys
from pathlib import Path
from typing import Dict, Set

from graph_tool import Graph, load_graph

from plwn_graph_builder.vertices import LexicalUnit, Synset

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)


class PLWNGraph:

    def __init__(self):
        self._db = None

        self.syn_G = Graph()
        self.lu_G = Graph()

        self._lu_dict = None
        self._syn_dict = None

        self._syn_to_vertex_dict = None
        self._lu_to_vertex_dict = None

    def load_syn_graph(self, syn_graph_file):
        self.syn_G = load_graph(syn_graph_file)

    def load_lu_graph(self, lu_graph_file):
        self.lu_G = load_graph(lu_graph_file)

    def build_graphs(self, db_connection):
        self._db = db_connection

        self._lu_dict = self._get_lexical_units()
        self._syn_dict = self._get_synsets()

        self._add_syn_vertices()
        self._add_lu_vertices()

        self._add_syn_edges()
        self._add_lu_edges()

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
            self._lu_dict[row.lu_id]
            for row in results
            if row.lu_id in self._lu_dict
        }
        results.close()

        return lexical_units


def _add_syn_vertices(self):
    self._syn_to_vertex_dict = {}

    vertex_prop = self.syn_G.new_vertex_property('python::object')
    for synset_id, synset in self._syn_dict.items():
        vertex = self.syn_G.add_vertex()
        vertex_prop[vertex] = synset
        self._syn_to_vertex_dict[synset_id] = vertex

    self.syn_G.vertex_properties['synset'] = vertex_prop


def _add_lu_vertices(self):
    self._lu_to_vertex_dict = {}

    vertex_prop = self.lu_G.new_vertex_property('python::object')
    for lu_id, lu in self._lu_dict.items():
        vertex = self.lu_G.add_vertex()
        vertex_prop[vertex] = lu
        self._lu_to_vertex_dict[lu_id] = vertex

    self.lu_G.vertex_properties['lu'] = vertex_prop


def _add_syn_edges(self):
    edge_prop_rel_id = self.syn_G.new_edge_property('int')

    try:
        with self._db.cursor() as cursor:
            sql_query = 'SELECT DISTINCT parent_id, child_id, rel_id FROM synsetrelation;'
            cursor.execute(sql_query)

            for row in cursor.fetchall():
                parent_id = row['parent_id']
                child_id = row['child_id']
                rel_id = row['rel_id']

                if parent_id in self._syn_to_vertex_dict:
                    vertex_parent_id = self._syn_to_vertex_dict[parent_id]
                else:
                    print(
                        f'A parent sysnet {parent_id} appears in synsetrelation table but is missing in synset table.',
                        file=sys.stderr)
                    continue

                if child_id in self._syn_to_vertex_dict:
                    vertex_child_id = self._syn_to_vertex_dict[child_id]
                else:
                    print(
                        f'A child sysnet {child_id} appears in synsetrelation table but is missing in synset table.',
                        file=sys.stderr)
                    continue

                edge = self.syn_G.add_edge(vertex_parent_id,
                                           vertex_child_id)
                edge_prop_rel_id[edge] = rel_id

            self.syn_G.edge_properties['rel_id'] = edge_prop_rel_id
    except Exception as e:
        print(e, file=sys.stderr)


def _add_lu_edges(self):
    edge_prop_rel_id = self.lu_G.new_edge_property('int')

    try:
        with self._db.cursor() as cursor:
            sql_query = 'SELECT DISTINCT parent_id, child_id, rel_id FROM lexicalrelation;'
            cursor.execute(sql_query)

            for row in cursor.fetchall():
                parent_id = row['parent_id']
                child_id = row['child_id']
                rel_id = row['rel_id']

                if parent_id in self._lu_to_vertex_dict:
                    vertex_parent_id = self._lu_to_vertex_dict[parent_id]
                else:
                    print(
                        f'A parent lexical unit {parent_id} appears in synsetrelation table but is missing in unitandsynset table.',
                        file=sys.stderr)
                    continue

                if child_id in self._lu_to_vertex_dict:
                    vertex_child_id = self._lu_to_vertex_dict[child_id]
                else:
                    print(
                        f'A child lexical unit {child_id} appears in synsetrelation table but is missing in unitandsynset table.',
                        file=sys.stderr)
                    continue

                edge = self.lu_G.add_edge(vertex_parent_id, vertex_child_id)
                edge_prop_rel_id[edge] = rel_id

            self.lu_G.edge_properties['rel_id'] = edge_prop_rel_id
    except Exception as e:
        print(e, file=sys.stderr)


def save_graphs(self, out_dir: Path):
    synset_graph_path = out_dir / 'plwn_graph_syn.xml.gz'
    self.syn_G.save(synset_graph_path)

    lu_graph_path = out_dir / 'plwn_graph_lu.xml.gz'
    self.lu_G.save(lu_graph_path)
