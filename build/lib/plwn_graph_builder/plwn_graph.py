import sys

from graph_tool import Graph, load_graph
from vertices.lexical_unit import LexicalUnit
from vertices.synset import Synset


class PLWNGraph:

    def __init__(self):
        self.dbconnection = None

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

    def build_graphs(self, dbconnection):
        self.dbconnection = dbconnection

        self._lu_dict = self._get_lu_dict()
        self._syn_dict = self._get_syn_dict()

        self._add_syn_vertices()
        self._add_lu_vertices()

        self._add_syn_edges()
        self._add_lu_edges()

    def _get_lu_dict(self):
        lu_dict = {}

        try:
            with self.dbconnection.cursor() as cursor:
                sql_query = 'SELECT DISTINCT id, lemma, domain, pos, variant, comment FROM lexicalunit;'
                cursor.execute(sql_query)

                for row in cursor.fetchall():
                    lu = LexicalUnit(
                        lu_id=row['id'],
                        lemma=row['lemma'],
                        pos=row['pos'],
                        domain=row['domain'],
                        variant=row['variant']
                    )

                    if lu.lu_id not in lu_dict:
                        lu_dict[lu.lu_id] = lu
                    else:
                        print(f'Multiple lexical unit has the same indetifier {lu.lu_id}.', file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)

        return lu_dict

    def _get_syn_dict(self):
        syn_dict = {}

        try:
            with self.dbconnection.cursor() as cursor:
                sql_query = 'SELECT DISTINCT id FROM synset;'
                cursor.execute(sql_query)

                for row in cursor.fetchall():
                    synset_id = row['id']
                    lu_set = self._get_lu_set(synset_id)

                    synset = Synset(
                        synset_id=synset_id,
                        lu_set=lu_set
                    )
                    syn_dict[synset_id] = synset
        except Exception as e:
            print(e, file=sys.stderr)

        return syn_dict

    def _get_lu_set(self, synset_id):
        lu_set = set()

        try:
            with self.dbconnection.cursor() as cursor:
                sql_query = f'SELECT DISTINCT lex_id FROM unitandsynset WHERE syn_id={str(synset_id)};'
                cursor.execute(sql_query)

                for row in cursor.fetchall():
                    lu_id = row['lex_id']

                    if lu_id in self._lu_dict:
                        lu_set.add(self._lu_dict[lu_id])
                    else:
                        print(
                            f'A lexical unit {lu_id} which appears in unitandsynset table is missing in lexicalunit table.',
                            file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)

        return lu_set

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
            with self.dbconnection.cursor() as cursor:
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

                    edge = self.syn_G.add_edge(vertex_parent_id, vertex_child_id)
                    edge_prop_rel_id[edge] = rel_id

                self.syn_G.edge_properties['rel_id'] = edge_prop_rel_id
        except Exception as e:
            print(e, file=sys.stderr)

    def _add_lu_edges(self):
        edge_prop_rel_id = self.lu_G.new_edge_property('int')

        try:
            with self.dbconnection.cursor() as cursor:
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

    def save_graphs(self, graphs_file):
        path_to_syn_graph = f"{graphs_file}_syn.xml.gz"
        self.syn_G.save(path_to_syn_graph)

        path_to_lu_graph = f"{graphs_file}_lu.xml.gz"
        self.lu_G.save(path_to_lu_graph)
