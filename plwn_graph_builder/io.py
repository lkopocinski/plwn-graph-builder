import logging

from pathlib import Path
from typing import Dict

import yaml


logging.basicConfig(level=logging.ERROR, format="%(message)s")
logger = logging.getLogger(__name__)


def load_yaml(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exception:
            logger.exception(exception)
            return {}
