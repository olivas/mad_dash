"""Functions for database dropdown menu."""

from typing import Dict, List

from ..utils import db


def get_database_name_options() -> List[Dict[str, str]]:
    """Return the databases available for selection in the dropdown menu."""
    database_names = db.get_database_names()
    return [{'value': n, 'label': n} for n in database_names]


def get_default_database() -> str:
    """Return the default database."""
    if len(get_database_name_options()) == 1:
        return get_database_name_options()[0]['label']
    return ''
