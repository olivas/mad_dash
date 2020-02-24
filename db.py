import logging
import os
import urllib


def create_simprod_db_client(database_url='mongodb-simprod.icecube.wisc.edu',
                             dbuser='DBadmin',
                             password_path=os.path.expandvars('$HOME/.mongo')):
    try:
        from pymongo import MongoClient
    except ImportError:
        logging.critical("PyMongo not installed.")

    if not os.path.exists(password_path):
        logging.critical(f"Password file '{password_path}' not found.")

    with open(password_path) as file:
        password = urllib.parse.quote_plus(file.readline().strip())
        uri = f"mongodb://{dbuser}:{password}@{database_url}"

    client = MongoClient(uri)

    return client


def get_database_names(database_url):
    """Return the database names."""
    client = create_simprod_db_client(database_url)
    excludes = ('system.indexes', 'admin', 'local', 'simprod_filecatalog')
    database_names = [n for n in client.database_names() if n not in excludes]
    return database_names


def get_database(database_name, database_url):
    """Return the database."""
    client = create_simprod_db_client(database_url)
    database = client[database_name]
    return database


def get_collection_names(database_name, database_url):
    """Return the database's collections."""
    database = get_database(database_name, database_url)
    collection_names = [n for n in database.collection_names() if n != 'system.indexes']
    return collection_names


def get_collection(collection_name, database_name, database_url):
    """Return the collection."""
    client = create_simprod_db_client(database_url)
    database = client[database_name]
    collection = database[collection_name]
    return collection


def get_histogram_names(collection_name, database_name, database_url):
    """Return the histograms names in the collection"""
    collection = get_collection(collection_name, database_name, database_url)
    cursor = collection.find()
    histogram_names = [d['name'] for d in cursor if d['name'] != 'filelist']
    return histogram_names


def get_histograms(collection_name, database_name, database_url):
    """Return the histograms from the collection."""
    collection = get_collection(collection_name, database_name, database_url)
    cursor = collection.find({})
    histograms = [d for d in cursor if d['name'] != 'filelist']
    return histograms


def get_histogram(histogram_name, collection_name, database_name, database_url):
    """Return the histogram."""
    collection = get_collection(collection_name, database_name, database_url)
    histogram = collection.find_one({'name': histogram_name})
    return histogram


def get_filelist(collection_name, database_name, database_url):
    """Return the filenames in the filelist from the collection."""
    collection = get_collection(collection_name, database_name, database_url)
    filelist = collection.find_one({'name': 'filelist'})['files']
    return filelist
