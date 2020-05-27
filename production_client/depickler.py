"""Ingest histograms from production histogram pickle(s) to database(s)."""

import argparse
import asyncio
import logging
import os
import pickle
import re
from typing import Iterator, List, Tuple
from urllib.parse import urljoin

import requests
from rest_tools.client import RestClient  # type: ignore


async def post_filelist(rc: RestClient, filelist: list, collection_name: str, database_name: str, update: bool=False) -> None:
    """POST filelist to collection in simprod mongo DBMS."""
    post_body = {'database': database_name,
                 'collection': collection_name,
                 'files': filelist,
                 'update': update}
    post_resp = await rc.request('POST', '/files/names', post_body)
    logging.info(f"POSTed filelist to {collection_name} (db: {database_name}).")
    logging.debug(f"POST response: {post_resp}.")


def get_filelist(collection: dict, collection_name: str) -> list:
    """Get the filelist in the collection."""
    filelist = collection['filelist']['files']
    if filelist:
        logging.info(f"From collection ('{collection_name}'), grabbed filelist ({len(filelist)} files).")
    else:
        logging.info(f"From collection ('{collection_name}'), no files in filelist.")
    return filelist


async def post_histogram(rc: RestClient, histo: dict, collection_name: str, database_name: str, update: bool=False) -> None:
    """POST histogram to collection in simprod mongo DBMS."""
    post_body = {'database': database_name,
                 'collection': collection_name,
                 'histogram': histo,
                 'update': update}
    post_resp = await rc.request('POST', '/histogram', post_body)
    logging.info(f"POSTed histogram ({histo['name']}) to {collection_name} (db: {database_name}).")
    logging.debug(f"POST response: {post_resp}.")


def get_each_histogram(collection: dict, collection_name: str) -> Iterator[dict]:
    """Get all histograms in collection."""
    for k, v in collection.items():
        if k == 'filelist':
            continue
        logging.debug(f"From collection ('{collection_name}'), grabbed histogram ('{v['name']}').")
        yield v


def get_all_pickles(paths: List[str], recurse: bool = False) -> List[str]:
    """Get all pickle files in paths."""
    pickles = []

    for p in paths:
        # is it a directory?
        if os.path.isdir(p):
            if recurse:
                logging.debug(f"Path is a directory, '{p}', getting it's files...")
                paths.extend(os.path.join(p, f) for f in os.listdir(p))
            else:
                raise RuntimeError(f"{p} is a directory. Run with -r to recursively find pickles.")
        # is it a file?
        elif os.path.isfile(p):
            logging.debug(f"Path is a file, '{p}'.")
            if p.endswith('.pkl'):
                pickles.append(p)
        # or something else?
        else:
            logging.debug(f"Path is not a file nor directory, '{p}'.")

    return pickles


def get_each_collection(paths: List[str], recurse: bool = False) -> Iterator[Tuple[dict, str]]:
    """Generate histograms and file-lists from pickles at given paths."""
    pickles = get_all_pickles(paths, recurse=recurse)

    for p in pickles:
        # depickle
        with open(p, 'rb') as f:
            collection = pickle.load(f)
        logging.debug(f"Depickled collection at {p}.")
        # get name
        name = re.findall(r'/([^/]*).pkl$', p)[0]
        logging.debug(f"Name for {p} is {name}.")
        # yield
        logging.info(f"Grabbed collection, {name}.")
        yield (collection, name)


def get_rest_client(dbms_url, token_url):
    """Get database REST client."""
    token_json = requests.get(urljoin(token_url, 'token?scope=maddash:production')).json()
    rc = RestClient(dbms_url, token=token_json['access'], timeout=5, retries=0)
    return rc


async def main() -> None:
    """Do main."""
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', metavar='PATHS', nargs='+',
                        help='path(s) to grab pickles;'
                        ' each filename will be used as a mongodb collection name.')
    parser.add_argument('-r', dest='recurse_paths', default=False, action='store_true',
                        help='recursively search for pickle files.')
    parser.add_argument('--database', default='simprod_histos',
                        help='name of database to ingest histograms.')
    parser.add_argument('-u', '--update', default=False, action='store_true',
                        help='update histogram, if it already exists in the database.')
    parser.add_argument('--dbms-url', dest='dbms_url', default='http://localhost:8080',
                        help='url to the dbms server.')
    parser.add_argument('--token-url', dest='token_url', default='http://localhost:8888',
                        help='url to the token service.')
    parser.add_argument('-l', '--log', default='DEBUG',
                        help='the output logging level')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper()))
    for arg, val in vars(args).items():
        logging.info(f"{arg}: {val}")

    rc = get_rest_client(args.dbms_url, args.token_url)
    for collection, name in get_each_collection(args.paths, args.recurse_paths):
        for h in get_each_histogram(collection, name):
            await post_histogram(rc, h, name, args.database)

        filelist = get_filelist(collection, name)
        if filelist:
            await post_filelist(rc, filelist, name, args.database)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
