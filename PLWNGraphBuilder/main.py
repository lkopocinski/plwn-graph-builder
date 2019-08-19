import argparse
import sys

import argcomplete
from database import DB
from plwn_graph import PLWNGraph


def make_parser():
    desc = 'PLWN graph builder.'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-d', '--db-config', dest='db_config', required=True)
    parser.add_argument('-is', '--in-syn-graph-file', dest='in_syn_graph_file', required=False)
    parser.add_argument('-il', '--in-lu-graph-file', dest='in_lu_graph_file', required=False)
    parser.add_argument('-o', '--out-graphs-file', dest='out_graphs_file', required=False)

    argcomplete.autocomplete(parser)
    return parser


def create_new_graphs(dbconfig, PLWN_G):
    db = DB()
    dbconnection = db.connect(dbconfig)
    if not dbconnection:
        print('Cannot connect to DB!', file=sys.stderr)
        exit(1)

    PLWN_G.build_graphs(dbconnection)


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)

    PLWN_G = PLWNGraph()

    if args.in_syn_graph_file:
        PLWN_G.load_syn_graph(args.in_syn_graph_file)

    if args.in_lu_graph_file:
        PLWN_G.load_lu_graph(args.in_lu_graph_file)

    if not args.in_syn_graph_file and not args.in_lu_graph_file:
        create_new_graphs(args.db_config, PLWN_G)

        if args.out_graphs_file:
            PLWN_G.save_graphs(args.out_graphs_file)


if __name__ == '__main__':
    main()
