from pathlib import Path

import click

from plwn_graph_builder.graph import LexicalUnitGraphBuilder, SynsetGraphBuilder
from plwn_graph_builder.plwn import PLWN


@click.command()
@click.option('--type', '-t', 'graph_type',
              required=True,
              type=click.Choice(['lexical', 'synset'], case_sensitive=False),
              help='Graph type to be build.')
@click.option('--db', 'db_config',
              required=True,
              type=click.Path(),
              help='Word Net database config file path.')
@click.option('--out', '-o', 'out_path',
              required=True,
              type=click.Path(exists=True),
              help='File path for saving created graph.')
def main(graph_type, db_config, out_path):
    plwn = PLWN(Path(db_config))

    if graph_type == 'lexical':
        graph_builder = LexicalUnitGraphBuilder(plwn=plwn)
    else:
        graph_builder = SynsetGraphBuilder(plwn=plwn)

    graph = graph_builder.build()
    graph.save(out_path, fmt='gt')


if __name__ == '__main__':
    main()
