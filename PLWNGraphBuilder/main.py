import sys
import argcomplete, argparse

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


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)

    PLWN_G = PLWNGraph()

    if args.in_syn_graph_file:
        PLWN_G.load_syn_graph(args.in_syn_graph_file)

    if args.in_lu_graph_file:
        PLWN_G.load_lu_graph(args.in_lu_graph_file)

    if not args.in_syn_graph_file and not args.in_lu_graph_file:
        print('Connecting to DB...', file=sys.stderr)
        db = DB()
        dbconnection = db.connect(args.db_config)
        if not dbconnection:
            print('Cannot connect to DB!', file=sys.stderr)
            exit(1)

        print('Done!', file=sys.stderr)

        PLWN_G.build_graphs(dbconnection)
        if args.out_graphs_file:
            PLWN_G.save_graphs(args.out_graphs_file)


if __name__ == '__main__':
    main()
