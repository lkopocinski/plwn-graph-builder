import sys
import argcomplete, argparse

from npsemrel.carrot.db import db

import plwn_graph
from plwn_graph import PLWNGraph


def make_parser():
    desc = 'PLWN graph builder...'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-d', '--db-config', dest='db_config', required=True)
    parser.add_argument('-is', '--in-syn-graph-file', dest='in_syn_graph_file', required=False)
    parser.add_argument('-il', '--in-lu-graph-file', dest='in_lu_graph_file', required=False)
    parser.add_argument('-o', '--out-graphs-file', dest='out_graphs_file', required=False)

    argcomplete.autocomplete(parser)
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)

    PLWN_G = PLWNGraph()

    if args.in_syn_graph_file:
        PLWN_G.load_syn_graph(args.in_syn_graph_file)

    if args.in_lu_graph_file:
        PLWN_G.load_lu_graph(args.in_lu_graph_file)

    if not args.in_syn_graph_file and not args.in_lu_graph_file:
        print >> sys.stderr, 'Connecting to DB...',
        dbcon = db.DB()
        dbconnection = dbcon.connect(args.db_config)
        if not dbconnection:
            print >> sys.stderr, 'Cannot connect to DB!'
            exit(1)
        print >> sys.stderr, ' Done!'

        PLWN_G.build_graphs(dbconnection)
        if args.out_graphs_file:
            PLWN_G.save_graphs(args.out_graphs_file)

    '''
    if PLWN_G.syn_G:
      print 'SYNSET GRAPH:'
      for v in PLWN_G.syn_G.vertices():
        print v, 'Synset:', PLWN_G.syn_G.vertex_properties["synset"][v].synset_id,
        for lu in PLWN_G.syn_G.vertex_properties["synset"][v].lu_set:
          print 'LU:', lu.lu_id, lu.lemma, lu.pos, lu.domain, lu.variant,
        print
      
      for e in PLWN_G.syn_G.edges():
        print e, PLWN_G.syn_G.edge_properties["rel_id"][e]
  
    if PLWN_G.lu_G:
      print 'LU GRAPH:'
      for v in PLWN_G.lu_G.vertices():
        print v, 'LU:', PLWN_G.lu_G.vertex_properties["lu"][v].lu_id, \
                        PLWN_G.lu_G.vertex_properties["lu"][v].lemma, \
                        PLWN_G.lu_G.vertex_properties["lu"][v].pos, \
                        PLWN_G.lu_G.vertex_properties["lu"][v].domain, \
                        PLWN_G.lu_G.vertex_properties["lu"][v].variant
      
      for e in PLWN_G.lu_G.edges():
        print e, PLWN_G.lu_G.edge_properties["rel_id"][e]
    '''


if __name__ == '__main__':
    main()
