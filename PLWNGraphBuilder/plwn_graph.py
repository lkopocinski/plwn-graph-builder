from __future__ import absolute_import

import sys

from PLWNGraphBuilder.vertices.lexical_unit import LexicalUnit
from PLWNGraphBuilder.vertices.synset import Synset

from graph_tool import Graph, load_graph



class PLWNGraph:

  def __init__(self):
    self.dbconnection = None

    self.syn_G = Graph()
    self.lu_G = Graph()

    self._lu_dict = None
    self._syn_dict = None

    self._syn_on_vertex_dict = None
    self._lu_on_vertex_dict = None

  def _get_lu_dict(self, comment=False):
    '''
    {lu_id_1: lu_object_1, lu_id_2: lu_object_2, ..., lu_id_N: lu_object_N}
    {..., 46469: <PLWNGraphBuilder.lexical_unit.LexicalUnit instance at 0x47a4878>, ...}
    '''
    lu_dict = {}

    sql_query = 'SELECT DISTINCT id, lemma, domain, pos, variant, comment ' \
                'FROM lexicalunit;'

    cursor = self.dbconnection.cursor()
    cursor.execute(sql_query)

    for row in cursor.fetchall():
      lu_id = int(row[0])
      lu_lemma = str(row[1].encode('utf-8'))
      lu_domain = int(row[2])
      lu_pos = int(row[3])
      lu_variant = int(row[4])

      lu_comment = str(row[5].encode('utf-8')) if comment else ''

      lu = LexicalUnit(
        lu_id, lu_lemma, lu_pos, lu_domain, lu_variant, comment=lu_comment
      )

      if lu_id not in lu_dict:
        lu_dict[lu_id] = lu
      else:
        print >> sys.stderr, 'W bazie danych Slowosieci powotrzyl sie', \
                             'identyfikator dla roznych jednostek leksykalnych!', \
                             '(' + lu_id + ')'
    return lu_dict

  def _get_syn_dict(self):
    '''
    {syn_id_1: syn_object_1, syn_id_2: syn_object_2, ..., syn_id_N: syn_object_N}
    {..., 30421: <PLWNGraphBuilder.synset.Synset instance at 0x82b1170>, ...}
    '''
    syn_dict = {}

    sql_query = 'SELECT DISTINCT id ' \
                'FROM synset;'

    cursor = self.dbconnection.cursor()
    cursor.execute(sql_query)

    for row in cursor.fetchall():
      synset_id = int(row[0])

      lu_set = set()
      lu_set = self._get_lu_set(synset_id)

      syn = Synset(synset_id, lu_set)
      syn_dict[synset_id] = syn

    return syn_dict

  def _get_lu_set(self, synset_id):
    '''
    Dla podanego na wejsciu identyfikatora synsetu
    zwraca zbior obiektow jednostek leksykalnych,
    ktore sie w nim zawieraja.
    '''
    lu_set = set()

    sql_query = 'SELECT DISTINCT LEX_ID ' \
                'FROM unitandsynset ' \
                'WHERE SYN_ID=' + str(synset_id) + ';'

    cursor = self.dbconnection.cursor()
    cursor.execute(sql_query)

    for row in cursor.fetchall():
      lu_id = int(row[0])

      if lu_id in self._lu_dict:
        lu_set.add(self._lu_dict[lu_id])
      else:
        print >> sys.stderr, 'W tabeli lexicalunit brakuje jednostki leksykalnej', lu_id, \
                             ', ktora pojawila sie w tabeli unitandsynset!'

    return lu_set

  # Dodawanie wierzcholkow do grafow.
  def _add_syn_vertices(self):
    '''
    {synset_id_1: vertex_id_1, synset_id_2: vertex_id_2, ..., synset_id_N: vertex_id_N}
    {..., 10: 0, 11: 1, ...}
    '''
    self._syn_on_vertex_dict = {}

    v_synset = self.syn_G.new_vertex_property("python::object")
    for synset_id, syn in self._syn_dict.iteritems():
      v = self.syn_G.add_vertex()
      v_synset[v] = syn
      self._syn_on_vertex_dict[synset_id] = v

    self.syn_G.vertex_properties["synset"] = v_synset

  def _add_lu_vertices(self):
    '''
    {lu_id_1: vertex_id_1,lu_id_2: vertex_id_2, ..., lu_id_N: vertex_id_N}
    {..., 11: 0, 12: 1, ...}
    '''
    self._lu_on_vertex_dict = {}

    v_lu = self.lu_G.new_vertex_property("python::object")
    for lu_id, lu in self._lu_dict.iteritems():
      v = self.lu_G.add_vertex()
      v_lu[v] = lu
      self._lu_on_vertex_dict[lu_id] = v

    self.lu_G.vertex_properties["lu"] = v_lu

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
      if parent_id in self._syn_on_vertex_dict:
        v_parent_id = self._syn_on_vertex_dict[parent_id]
      else:
        print >> sys.stderr, 'Synset rodzic', parent_id, 'pojawil sie w tabeli ' \
                             'synsetrelation, a brakuje go w tabeli synset!'
        continue

      v_child_id = None
      if child_id in self._syn_on_vertex_dict:
        v_child_id = self._syn_on_vertex_dict[child_id]
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
      if parent_id in self._lu_on_vertex_dict:
        v_parent_id = self._lu_on_vertex_dict[parent_id]
      else:
        print >> sys.stderr, 'Synset rodzic', parent_id, 'pojawil sie w tabeli ' \
                             'lexicalrelation, a brakuje go w tabeli lexicalunit!'
        continue

      v_child_id = None
      if child_id in self._lu_on_vertex_dict:
        v_child_id = self._lu_on_vertex_dict[child_id]
      else:
        print >> sys.stderr, 'Synset dziecko', child_id, 'pojawil sie w tabeli ' \
                             'lexicalrelation, a brakuje go w tabeli lexicalunit!'
        continue

      e = self.lu_G.add_edge(v_parent_id, v_child_id)
      e_rel_id[e] = rel_id

    self.lu_G.edge_properties["rel_id"] = e_rel_id

  def build_graphs(self, dbconnection):
    self.dbconnection = dbconnection

    self._lu_dict = self._get_lu_dict()
    self._syn_dict = self._get_syn_dict()

    print >> sys.stderr, 'Add syn vertices...',
    self._add_syn_vertices()
    print >> sys.stderr, 'Done!'
    print >> sys.stderr, 'Add lu vertices...',
    self._add_lu_vertices()
    print >> sys.stderr, 'Done!'

    print >> sys.stderr, 'Add syn edges...',
    self._add_syn_edges()
    print >> sys.stderr, 'Done!'
    print >> sys.stderr, 'Add lu edges...',
    self._add_lu_edges()
    print >> sys.stderr, 'Done!'

  def save_graphs(self, out_graphs_file):
    print >> sys.stderr, 'Save syn graph to file...',
    path_to_syn_graph = out_graphs_file + '_syn.xml.gz'
    self.syn_G.save(path_to_syn_graph)
    print >> sys.stderr, 'Done!'

    print >> sys.stderr, 'Save lu graph to file...',
    path_to_lu_graph = out_graphs_file + '_lu.xml.gz'
    self.lu_G.save(path_to_lu_graph)
    print >> sys.stderr, 'Done!'

  def load_syn_graph(self, in_syn_graph_file):
    print >> sys.stderr, 'Load syn graph from file...',
    self.syn_G = load_graph(in_syn_graph_file)
    print >> sys.stderr, 'Done!'

  def load_lu_graph(self, in_lu_graph_file):
    print >> sys.stderr, 'Load lu graph from file...',
    self.lu_G = load_graph(in_lu_graph_file)
    print >> sys.stderr, 'Done!'
