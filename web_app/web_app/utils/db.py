"""Contains functions for querying the database(s)."""
import logging
import os
from typing import List
from urllib.parse import urljoin

import requests
from rest_tools.client import RestClient


def create_simprod_dbms_rest_connection(dbms_server_url: str = 'http://localhost:8080',
                                        token_server_url: str = 'http://localhost:8888/') -> RestClient:
    """Return REST Client connection object."""
    token_request_url = urljoin(token_server_url, 'token?scope=maddash:web')

    token_json = requests.get(token_request_url).json()
    md_rc = RestClient(dbms_server_url, token=token_json['access'], timeout=5, retries=0)

    return md_rc


def get_database_names() -> List[dict]:
    """Return the database names."""
    md_rc = create_simprod_dbms_rest_connection()
    databases = md_rc.request_seq('GET', '/databases/names')

    return sorted(databases['databases'])


def get_collection_names(database_name: str) -> List[str]:
    """Return the database's collections."""
    if not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    db_request_body = {'database': database_name}
    collections = md_rc.request_seq('GET', '/collections/names', db_request_body)

    return sorted(collections['collections'])


def get_histogram_names(collection_name: str, database_name: str) -> List[str]:
    """Return the histograms names in the collection."""
    if not collection_name or not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    coll_request_body = {'database': database_name, 'collection': collection_name}
    histograms = md_rc.request_seq('GET', '/collections/histograms/names', coll_request_body)

    return sorted(histograms['histograms'])


def get_histograms(collection_name: str, database_name: str) -> List[dict]:
    """Return the histograms from the collection."""
    if not collection_name or not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    coll_histos_request_body = {'database': database_name,
                                'collection': collection_name}
    histograms = md_rc.request_seq('GET', '/collections/histograms', coll_histos_request_body)

    return histograms['histograms']


def get_histogram(histogram_name: str, collection_name: str, database_name: str) -> dict:
    """Return the histogram."""
    if not histogram_name or not collection_name or not database_name:
        return dict()

    md_rc = create_simprod_dbms_rest_connection()
    histo_request_body = {'database': database_name,
                          'collection': collection_name,
                          'name': histogram_name}
    try:
        histogram = md_rc.request_seq('GET', '/histogram', histo_request_body)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return dict()

    return histogram['histogram']


def get_filelist(collection_name: str, database_name: str) -> List[str]:
    """Return the filenames in the filelist from the collection."""
    if not collection_name or not database_name:
        return []

    md_rc = create_simprod_dbms_rest_connection()
    coll_request_body = {'database': database_name, 'collection': collection_name}
    filelist = md_rc.request_seq('GET', '/files/names', coll_request_body)

    return filelist['files']
