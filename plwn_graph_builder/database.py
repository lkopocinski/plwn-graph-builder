from pathlib import Path
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL

from plwn_graph_builder.utils import load_yaml


def _parse_config(path: Path) -> Dict:
    return load_yaml(path)


def get_engine(config_path: Path) -> Engine:
    config = _parse_config(config_path)
    url = URL(**config)
    return create_engine(url, echo=True)
