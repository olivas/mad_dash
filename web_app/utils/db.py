"""Contains functions for querying the database(s)."""

import logging
from typing import List
from urllib.parse import urljoin

import requests
from rest_tools.client import RestClient  # type: ignore

from ..config import dbms_server_url, token_server_url


def create_simprod_dbms_rest_connection() -> RestClient:
    """Return REST Client connection object."""
    token_request_url = urljoin(token_server_url, 'token?scope=maddash:web')

    token_json = requests.get(token_request_url).json()
    md_rc = RestClient(dbms_server_url, token=token_json['access'], timeout=5, retries=0)

    return md_rc


def _log(url, database="", collection="", histogram=""):
    db_str = coll_str = histo_str = ''
    if database:
        db_str = f"(db: {database})"
    if collection:
        coll_str = f"(co: {collection})"
    if histogram:
        histo_str = f"(hi: {histogram})"

    logging.info(f"DB REST Call: {url} {db_str} {coll_str} {histo_str}")


def get_database_names() -> List[str]:
    """Return the database names."""
    md_rc = create_simprod_dbms_rest_connection()
    url = '/databases/names'
    response = md_rc.request_seq('GET', url)

    _log(url)
    return sorted(response['databases'])


def get_collection_names(database_name: str) -> List[str]:
    """Return the database's collections."""
    if not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    db_request_body = {'database': database_name}
    url = '/collections/names'
    response = md_rc.request_seq('GET', url, db_request_body)

    _log(url, database_name)
    return sorted(response['collections'])


def get_histogram_names(collection_name: str, database_name: str) -> List[str]:
    """Return the histograms names in the collection."""
    if not collection_name or not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    coll_request_body = {'database': database_name, 'collection': collection_name}
    url = '/collections/histograms/names'
    response = md_rc.request_seq('GET', url, coll_request_body)

    _log(url, database_name, collection_name)
    return sorted(response['histograms'])


def get_histograms(collection_name: str, database_name: str) -> List[dict]:
    """Return the histograms from the collection."""
    if not collection_name or not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    coll_histos_request_body = {'database': database_name,
                                'collection': collection_name}
    url = '/collections/histograms'
    response = md_rc.request_seq('GET', url, coll_histos_request_body)

    _log(url, database_name, collection_name)
    return response['histograms']


def get_histogram(histogram_name: str, collection_name: str, database_name: str) -> dict:
    """Return the histogram."""
    if not histogram_name or not collection_name or not database_name:
        return {}

    md_rc = create_simprod_dbms_rest_connection()
    histo_request_body = {'database': database_name,
                          'collection': collection_name,
                          'name': histogram_name}
    url = '/histogram'
    try:
        response = md_rc.request_seq('GET', url, histo_request_body)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return {}

    _log(url, database_name, collection_name, histogram_name)
    histogram = response['histogram']
    histogram['collection'] = collection_name
    return histogram


def get_filelist(collection_name: str, database_name: str) -> List[str]:
    """Return the filenames in the filelist from the collection."""
    if not collection_name or not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    coll_request_body = {'database': database_name, 'collection': collection_name}
    url = '/files/names'
    response = md_rc.request_seq('GET', url, coll_request_body)

    _log(url, database_name, collection_name)
    return response['files']
