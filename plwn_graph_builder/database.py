from pathlib import Path
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from plwn_graph_builder.utils import load_yaml


def _parse_config(path: Path) -> Dict:
    return load_yaml(path)


def connect(config_path: Path):
    config = _parse_config(config_path)
    url = URL(**config)
    return create_engine(url)
