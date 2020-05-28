"""Contains functions for querying the database(s)."""
import logging
import os
import urllib

import requests
from rest_tools.client import RestClient


def create_simprod_dbms_rest_connection(dbms_server_url='http://localhost:8080',
                                        token_server_url='http://localhost:8888/'):
    """Return REST Client connection object."""
    token_request_url = urllib.parse.urljoin(token_server_url, 'token?scope=maddash:web')

    token_json = requests.get(token_request_url).json()
    md_rc = RestClient(dbms_server_url, token=token_json['access'], timeout=5, retries=0)

    return md_rc


def get_database_names(database_url):
    """Return the database names."""
    md_rc = create_simprod_dbms_rest_connection()
    databases = md_rc.request_seq('GET', '/databases/names')

    return sorted(databases['databases'])


def get_collection_names(database_name, database_url):
    """Return the database's collections."""
    md_rc = create_simprod_dbms_rest_connection()
    db_request_body = {'database': database_name}
    collections = md_rc.request_seq('GET', '/collections/names', db_request_body)

    return sorted(collections['collections'])


def get_histogram_names(collection_name, database_name, database_url):
    """Return the histograms names in the collection."""
    md_rc = create_simprod_dbms_rest_connection()
    coll_request_body = {'database': database_name, 'collection': collection_name}
    histograms = md_rc.request_seq('GET', '/collections/histograms/names', coll_request_body)

    return sorted(histograms['histograms'])


def get_histograms(collection_name, database_name, database_url):
    """Return the histograms from the collection."""
    md_rc = create_simprod_dbms_rest_connection()
    coll_histos_request_body = {'database': database_name,
                                'collection': collection_name}
    histograms = md_rc.request_seq('GET', '/collections/histograms', coll_histos_request_body)

    return histograms['histograms']


def get_histogram(histogram_name, collection_name, database_name, database_url):
    """Return the histogram."""
    md_rc = create_simprod_dbms_rest_connection()
    histo_request_body = {'database': database_name,
                          'collection': collection_name,
                          'name': histogram_name}
    try:
        histogram = md_rc.request_seq('GET', '/histogram', histo_request_body)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return None

    return histogram['histogram']


def get_filelist(collection_name, database_name, database_url):
    """Return the filenames in the filelist from the collection."""
    md_rc = create_simprod_dbms_rest_connection()
    coll_request_body = {'database': database_name, 'collection': collection_name}
    filelist = md_rc.request_seq('GET', '/files/names', coll_request_body)

    return filelist['files']
