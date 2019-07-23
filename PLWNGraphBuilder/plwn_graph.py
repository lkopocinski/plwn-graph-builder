import sys

from vertices.lexical_unit import LexicalUnit
from vertices.synset import Synset

from graph_tool import Graph, load_graph


class PLWNGraph:

  def __init__(self):
    self.dbconnection = None

    self.syn_G = Graph()
    self.lu_G = Graph()

    self._lu_dict = None
    self._syn_dict = None

    self._syn_to_vertex_dict = None
    self._lu_to_vertex_dict = None

  def _get_lu_dict(self, comment=False):
    """
    {lu_id_1: lu_object_1, lu_id_2: lu_object_2, ..., lu_id_N: lu_object_N}
    {..., 46469: <PLWNGraphBuilder.lexical_unit.LexicalUnit instance at 0x47a4878>, ...}
    """
    lu_dict = {}

    try:
      with self.dbconnection.cursor() as cursor:
        sql_query = 'SELECT DISTINCT id, lemma, domain, pos, variant, comment FROM lexicalunit;'
        cursor.execute(sql_query)

        for row in cursor.fetchall():
          lu = LexicalUnit(
            lu_id = row['id'],
            lemma = row['lemma'],
            pos = row['pos'],
            domain = row['domain'],
            variant = row['variant']
          )

          if lu.lu_id not in lu_dict:
            lu_dict[lu.lu_id] = lu
          else:
            print(f'Multiple lexical unit has the same indetifier {lu.lu_id}.', file=sys.stderr)
    except Exception as e:
      print(e)

    return lu_dict

  def _get_syn_dict(self):
    """
    {syn_id_1: syn_object_1, syn_id_2: syn_object_2, ..., syn_id_N: syn_object_N}
    {..., 30421: <PLWNGraphBuilder.synset.Synset instance at 0x82b1170>, ...}
    """
    syn_dict = {}

    try:
      with self.dbconnection.cursor() as cursor:
        sql_query = 'SELECT DISTINCT id FROM synset;'
        cursor.execute(sql_query)

        for row in cursor.fetchall():
          synset_id = row['id']
          lu_set = self._get_lu_set(synset_id)

          syn = Synset(synset_id, lu_set)
          syn_dict[synset_id] = syn
    except Exception as e:
      print(e)

    return syn_dict

  def _get_lu_set(self, synset_id):
    """
    For given sysnet id returns a set of lexical units object belongs to synset.
    """
    lu_set = set()

    try:
      with self.dbconnection.cursor() as cursor:
        sql_query = f'SELECT DISTINCT LEX_ID FROM unitandsynset WHERE SYN_ID={str(synset_id)};'
        cursor.execute(sql_query)

        for row in cursor.fetchall():
          lu_id = row['LEX_ID']

          if lu_id in self._lu_dict:
            lu_set.add(self._lu_dict[lu_id])
          else:
            print(f'A lexical unit {lu_id} which appears in unitandsynset table is missing in lexicalunit table.', file=sys.stderr)
    except Exception as e:
      print(e)

    return lu_set

  def _add_syn_vertices(self):
    """
    {synset_id_1: vertex_id_1, synset_id_2: vertex_id_2, ..., synset_id_N: vertex_id_N}
    {..., 10: 0, 11: 1, ...}
    """
    self._syn_to_vertex_dict = {}

    vertex_prop = self.syn_G.new_vertex_property('python::object')
    for synset_id, synset in self._syn_dict.items():
      vertex = self.syn_G.add_vertex()
      vertex_prop[vertex] = synset
      self._syn_to_vertex_dict[synset_id] = vertex

    self.syn_G.vertex_properties['synset'] = vertex_prop

  def _add_lu_vertices(self):
    '''
    {lu_id_1: vertex_id_1,lu_id_2: vertex_id_2, ..., lu_id_N: vertex_id_N}
    {..., 11: 0, 12: 1, ...}
    '''
    self._lu_to_vertex_dict = {}

    vertex_prop = self.lu_G.new_vertex_property('python::object')
    for lu_id, lu in self._lu_dict.iteritems():
      vertex = self.lu_G.add_vertex()
      vertex_prop[vertex] = lu
      self._lu_to_vertex_dict[lu_id] = vertex

    self.lu_G.vertex_properties['lu'] = vertex_prop

  # Dodawanie krawedzi do grafow.
  def _add_syn_edges(self):
    e_rel_id = self.syn_G.new_edge_property("int")

    sql_query = 'SELECT DISTINCT PARENT_ID, CHILD_ID, REL_ID ' \
                'FROM synsetrelation;'

    cursor = self.dbconnection.cursor()
    cursor.execute(sql_query)

    for row in cursor.fetchall():
      parent_id = int(row[0])
      child_id = int(row[1])
      rel_id = int(row[2])

      v_parent_id = None
      if parent_id in self._syn_to_vertex_dict:
        v_parent_id = self._syn_to_vertex_dict[parent_id]
      else:
        print >> sys.stderr, 'Synset rodzic', parent_id, 'pojawil sie w tabeli ' \
                             'synsetrelation, a brakuje go w tabeli synset!'
        continue

      v_child_id = None
      if child_id in self._syn_to_vertex_dict:
        v_child_id = self._syn_to_vertex_dict[child_id]
      else:
        print >> sys.stderr, 'Synset dziecko', child_id, 'pojawil sie w tabeli ' \
                             'synsetrelation, a brakuje go w tabeli synset!'
        continue

      e = self.syn_G.add_edge(v_parent_id, v_child_id)
      e_rel_id[e] = rel_id

    self.syn_G.edge_properties["rel_id"] = e_rel_id

  def _add_lu_edges(self):
    e_rel_id = self.lu_G.new_edge_property("int")

    sql_query = 'SELECT DISTINCT PARENT_ID, CHILD_ID, REL_ID ' \
                'FROM lexicalrelation;'

    cursor = self.dbconnection.cursor()
    cursor.execute(sql_query)

    for row in cursor.fetchall():
      parent_id = int(row[0])
      child_id = int(row[1])
      rel_id = int(row[2])

      v_parent_id = None
      if parent_id in self._lu_to_vertex_dict:
        v_parent_id = self._lu_to_vertex_dict[parent_id]
      else:
        print >> sys.stderr, 'Synset rodzic', parent_id, 'pojawil sie w tabeli ' \
                             'lexicalrelation, a brakuje go w tabeli lexicalunit!'
        continue

      v_child_id = None
      if child_id in self._lu_to_vertex_dict:
        v_child_id = self._lu_to_vertex_dict[child_id]
      else:
        print('Synset dziecko', child_id, 'pojawil sie w tabeli ' \
                             'lexicalrelation, a brakuje go w tabeli lexicalunit!')
        continue

      e = self.lu_G.add_edge(v_parent_id, v_child_id)
      e_rel_id[e] = rel_id

    self.lu_G.edge_properties["rel_id"] = e_rel_id

  def build_graphs(self, dbconnection):
    self.dbconnection = dbconnection

    self._lu_dict = self._get_lu_dict()
    self._syn_dict = self._get_syn_dict()

    self._add_syn_vertices()
    self._add_lu_vertices()

    self._add_syn_edges()
    self._add_lu_edges()

  def save_graphs(self, graphs_file):
    path_to_syn_graph = f"{graphs_file}_syn.xml.gz'"
    self.syn_G.save(path_to_syn_graph)

    path_to_lu_graph = f"{graphs_file}_lu.xml.gz"
    self.lu_G.save(path_to_lu_graph)

  def load_syn_graph(self, syn_graph_file):
    self.syn_G = load_graph(syn_graph_file)

  def load_lu_graph(self, lu_graph_file):
    self.lu_G = load_graph(lu_graph_file)
