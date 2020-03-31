from pathlib import Path

import click

from plwn_graph_builder.database import connect
from plwn_graph_builder.graph import PLWNGraph


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
    db = connect(Path(db_config))

    plwn_graph = PLWNGraph()
    plwn_graph.build_graphs(db)
    plwn_graph.save_graphs(output_dir)


if __name__ == '__main__':
    main()
