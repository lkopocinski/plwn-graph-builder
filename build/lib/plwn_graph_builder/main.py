import argparse
import sys

import argcomplete
from database import DB
from plwn_graph import PLWNGraph


def make_parser():
    desc = 'PLWN graph builder.'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-d', '--db-config', dest='db_config', required=True)
    parser.add_argument('-o', '--out-graph-file-prefix', dest='out_graph_file_prefix', required=True)

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
    create_new_graphs(args.db_config, PLWN_G)
    PLWN_G.save_graphs(args.out_graph_file_prefix)


if __name__ == '__main__':
    main()
