import logging

from abc import ABC, abstractmethod
from typing import Dict, Set, Tuple

from graph_tool import Graph, Vertex
from plwn_graph_builder.plwn import PLWN
from plwn_graph_builder.vertices import LexicalUnit


logging.basicConfig(level=logging.ERROR, format="%(message)s")
logger = logging.getLogger(__name__)


class GraphBuilder(ABC):
    EDGE_PROPERTY_TYPE = "int"
    VERTEX_PROPERTY_TYPE = "python::object"
    RELATION_PROPERTY_KEY = "relation_id"

    def __init__(self, plwn: PLWN):
        self._plwn = plwn
        self._graph: Graph

    @abstractmethod
    def build(self) -> Graph:
        ...

    @abstractmethod
    def _add_vertices(self):
        ...

    @abstractmethod
    def _add_edges(self):
        ...


class LexicalUnitGraphBuilder(GraphBuilder):
    LEXICAL_UNIT_PROPERTY_KEY = "lexical_unit"

    def __init__(self, plwn: PLWN):
        super().__init__(plwn)
        self._lexical_units_dict: Dict[int, LexicalUnit]
        self._lexical_unit_id_to_vertex_dict: Dict[int, Vertex]
        self._lexical_units_relations: Set[Tuple[int, int, int]]

    def build(self) -> Graph:
        self._graph = Graph()
        self._lexical_units_dict = self._plwn.lexical_units()
        self._lexical_units_relations = self._plwn.lexical_units_relations()

        self._add_vertices()
        self._add_edges()

        return self._graph

    def _add_vertices(self) -> None:
        self._lexical_unit_id_to_vertex_dict = {}

        vertex_property = self._graph.new_vertex_property(self.VERTEX_PROPERTY_TYPE)
        for lexical_unit_id, lexical_unit in self._lexical_units_dict.items():
            vertex = self._graph.add_vertex()
            vertex_property[vertex] = lexical_unit
            self._lexical_unit_id_to_vertex_dict[lexical_unit_id] = vertex

        self._graph.vertex_properties[self.LEXICAL_UNIT_PROPERTY_KEY] = vertex_property

    def _add_edges(self):
        edge_property = self._graph.new_edge_property(self.EDGE_PROPERTY_TYPE)

        for parent_id, child_id, relation_id in self._lexical_units_relations:
            parent_vertex = self._lexical_unit_id_to_vertex_dict.get(parent_id, None)
            child_vertex = self._lexical_unit_id_to_vertex_dict(child_id, None)

            if parent_vertex and child_vertex:
                edge = self._graph.add_edge(parent_vertex, child_vertex)
                edge_property[edge] = relation_id

        self._graph.edge_properties[self.RELATION_PROPERTY_KEY] = edge_property


class SynsetGraphBuilder(GraphBuilder):
    SYNSET_PROPERTY_KEY = "synset"

    def __init__(self, plwn: PLWN):
        super().__init__(plwn)
        self._synsets_dict: Dict[int, Set[LexicalUnit]]
        self._synset_id_to_vertex_dict: Dict[int, Vertex]
        self._synsets_relations: Set[Tuple[int, int, int]]

    def build(self) -> Graph:
        self._graph = Graph()
        self._synsets_dict = self._plwn.synsets()
        self._synsets_relations = self._plwn.synsets_relations()

        self._add_vertices()
        self._add_edges()

        return self._graph

    def _add_vertices(self):
        self._synset_id_to_vertex_dict = {}

        vertex_property = self._graph.new_vertex_property(self.VERTEX_PROPERTY_TYPE)
        for synset_id, synset in self._synsets_dict.items():
            vertex = self._graph.add_vertex()
            vertex_property[vertex] = synset
            self._synset_id_to_vertex_dict[synset_id] = vertex

        self._graph.vertex_properties[self.SYNSET_PROPERTY_KEY] = vertex_property

    def _add_edges(self):
        edge_property = self._graph.new_edge_property(self.EDGE_PROPERTY_TYPE)

        for parent_id, child_id, relation_id in self._synsets_relations:
            parent_vertex = self._synset_id_to_vertex_dict.get(parent_id, None)
            child_vertex = self._synset_id_to_vertex_dict.get(child_id, None)

            if parent_vertex and child_vertex:
                edge = self._graph.add_edge(parent_vertex, child_vertex)
                edge_property[edge] = relation_id

        self._graph.edge_properties[self.RELATION_PROPERTY_KEY] = edge_property
