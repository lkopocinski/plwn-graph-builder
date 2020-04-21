from pathlib import Path

import click

from plwn_graph_builder.graph import LexicalUnitGraphBuilder, SynsetGraphBuilder
from plwn_graph_builder.plwn import PLWN


@click.command()
@click.option('--db-config',
              required=True,
              type=click.Path(exists=True),
              help='Database config file path.')
@click.option('--output-dir',
              required=True,
              type=click.Path(exists=True),
              help='Directory for saving created graphs.')
def main(db_config, output_dir):
    plwn = PLWN(Path(db_config))

    graph_builder = LexicalUnitGraphBuilder(db=plwn)
    graph = graph_builder.build()
    graph.save('plwn_graph_lexical_units.xml.gz')

    graph_builder = SynsetGraphBuilder(db=plwn)
    graph = graph_builder.build()
    graph.save('plwn_graph_synset.xml.gz')


if __name__ == '__main__':
    main()
