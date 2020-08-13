"""Contains functions for querying the database(s)."""

import logging
import typing
from typing import List, Optional
from urllib.parse import urljoin

import requests

# local imports
import api
from rest_tools.client import RestClient  # type: ignore

from ..config import dbms_server_url, token_server_url


def create_simprod_dbms_rest_connection() -> RestClient:
    """Return REST Client connection object."""
    token_request_url = urljoin(token_server_url, "token?scope=maddash:web")

    token_json = requests.get(token_request_url).json()
    rc = RestClient(dbms_server_url, token=token_json["access"], timeout=5, retries=0)

    return rc


def _log(
    url: str, database: str = "", collection: str = "", histogram: str = ""
) -> None:
    db_str = coll_str = histo_str = ""
    if database:
        db_str = f"(db: {database})"
    if collection:
        coll_str = f"(co: {collection})"
    if histogram:
        histo_str = f"(hi: {histogram})"

    logging.info(f"DB REST Call: {url} {db_str} {coll_str} {histo_str}")


def get_database_names() -> List[str]:
    """Return the database names."""
    rc = create_simprod_dbms_rest_connection()
    url = "/databases/names"
    response = rc.request_seq("GET", url)

    _log(url)
    return sorted(response["databases"])


def get_collection_names(database_name: str) -> List[str]:
    """Return the database's collections."""
    if not database_name:
        return []

    rc = create_simprod_dbms_rest_connection()
    db_request_body = {"database": database_name}
    url = "/collections/names"
    response = rc.request_seq("GET", url, db_request_body)

    _log(url, database_name)
    return sorted(response["collections"])


def get_histogram_names(collection_name: str, database_name: str) -> List[str]:
    """Return the histograms names in the collection."""
    if not collection_name or not database_name:
        return []

    rc = create_simprod_dbms_rest_connection()
    coll_request_body = {"database": database_name, "collection": collection_name}
    url = "/collections/histograms/names"
    response = rc.request_seq("GET", url, coll_request_body)

    _log(url, database_name, collection_name)
    return sorted(response["histograms"])


def get_histograms(collection_name: str, database_name: str) -> List[api.I3Histogram]:
    """Return the histograms from the collection."""
    if not collection_name or not database_name:
        return []

    rc = create_simprod_dbms_rest_connection()
    coll_histos_request_body = {
        "database": database_name,
        "collection": collection_name,
    }
    url = "/collections/histograms"
    response = rc.request_seq("GET", url, coll_histos_request_body)

    _log(url, database_name, collection_name)
    return [api.I3Histogram.from_dict(h) for h in response["histograms"]]


def get_histogram(
    histogram_name: str, collection_name: str, database_name: str
) -> Optional[api.I3Histogram]:
    """Return the histogram."""
    if not histogram_name or not collection_name or not database_name:
        return None

    rc = create_simprod_dbms_rest_connection()
    histo_request_body = {
        "database": database_name,
        "collection": collection_name,
        "name": histogram_name,
    }
    url = "/histogram"
    try:
        response = rc.request_seq("GET", url, histo_request_body)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return None

    _log(url, database_name, collection_name, histogram_name)
    i3histo = api.I3Histogram.from_dict(response["histogram"])
    i3histo.collection = collection_name  # type: ignore
    return i3histo


def get_filelist(collection_name: str, database_name: str) -> List[str]:
    """Return the filenames in the filelist from the collection."""
    if not collection_name or not database_name:
        return []

    rc = create_simprod_dbms_rest_connection()
    coll_request_body = {"database": database_name, "collection": collection_name}
    url = "/files/names"
    response = rc.request_seq("GET", url, coll_request_body)

    _log(url, database_name, collection_name)
    files = response["files"]
    api.check_type(files, list, str)  # actually type check
    return typing.cast(List[str], files)  # type check for mypy
