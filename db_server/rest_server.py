"""Mad-Dash REST API server interface."""

import asyncio
import logging
from urllib.parse import quote_plus

import tornado.web
from motor.motor_tornado import MotorClient, MotorDatabase
from rest_tools.client import json_decode
from rest_tools.server import RestHandler, RestHandlerSetup, RestServer, from_environment, handler

AUTH_PREFIX = "maddash"

EXPECTED_CONFIG = {
    'MAD_DASH_AUTH_ALGORITHM': 'HS512',  # 'RS256',
    'MAD_DASH_AUTH_ISSUER': 'http://localhost:8888',  # 'maddash',
    'MAD_DASH_AUTH_SECRET': 'secret',
    'MAD_DASH_MONGODB_AUTH_USER': '',  # None means required to specify
    'MAD_DASH_MONGODB_AUTH_PASS': '',  # empty means no authentication required
    # 'MAD_DASH_MONGODB_DATABASE_NAME': 'lta',
    'MAD_DASH_MONGODB_HOST': 'localhost',
    'MAD_DASH_MONGODB_PORT': '27017',
    'MAD_DASH_REST_HOST': 'localhost',
    'MAD_DASH_REST_PORT': '8080',
}

# -----------------------------------------------------------------------------


class BaseMadDashHandler(RestHandler):
    """BaseMadDashHandler is a RestHandler for all Mad-Dash routes."""

    def initialize(self, db_client, *args, **kwargs):  # pylint: disable=W0221
        """Initialize a BaseMadDashHandler object."""
        super(BaseMadDashHandler, self).initialize(*args, **kwargs)
        self.db_client = db_client  # pylint: disable=W0201

    def get_database(self, database_name):
        """Return database instance."""
        try:
            return self.db_client[database_name]
        except KeyError:
            raise tornado.web.HTTPError(400, reason=f"database not found ({database_name})")

    def get_collection(self, database_name, collection_name):
        """Return collection instance."""
        database = self.get_database(database_name)
        try:
            return database[collection_name]
        except KeyError:
            raise tornado.web.HTTPError(400, reason=f"collection not found ({collection_name})")

    async def get_collection_contents(self, database_name, collection_name):
        """Return collection's contents."""
        collection = self.get_collection(database_name, collection_name)
        objs = []
        async for o in collection.find():
            objs.append(o)
        return objs

# -----------------------------------------------------------------------------


class MainHandler(BaseMadDashHandler):
    """MainHandler is a BaseMadDashHandler that handles the root route."""

    def get(self):
        """Handle GET."""
        self.write({})

# -----------------------------------------------------------------------------


class DatabasesHandler(BaseMadDashHandler):
    """Handle querying list of databases in mongodb client."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self):
        """Handle GET."""
        excludes = ['system.indexes', 'admin', 'local', 'simprod_filecatalog']
        database_names = [n for n in await self.db_client.list_database_names() if n not in excludes]

        self.write({'databases': database_names})

# -----------------------------------------------------------------------------


class CollectionsHandler(BaseMadDashHandler):
    """Handle querying list of collections from specified database."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self, database_name):
        """Handle GET."""
        database = super().get_database(database_name)
        collection_names = [n for n in await database.list_collection_names() if n != 'system.indexes']

        self.write({'database': database_name,
                    'collections': collection_names})

# -----------------------------------------------------------------------------


class HistogramsHandler(BaseMadDashHandler):
    """Handle querying list of histograms' names."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self, database_name, collection_name):
        """Handle GET."""
        collection_contents = await super().get_collection_contents(database_name, collection_name)
        histogram_names = [d['name'] for d in collection_contents if d['name'] != 'filelist']

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histograms': histogram_names})

# -----------------------------------------------------------------------------


class HistogramObjectHandler(BaseMadDashHandler):
    """Handle querying/adding histogram object."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self, database_name, collection_name, histogram_name):
        """Handle GET."""
        collection = super().get_collection(database_name, collection_name)
        try:
            histogram = await collection.find_one({'name': histogram_name})
        except StopIteration:
            raise tornado.web.HTTPError(400, reason=f"histogram not found ({histogram_name})")

        histogram = {k: histogram[k] for k in histogram if k != '_id'}

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': histogram})

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin'])
    async def post(self, database_name, collection_name, histogram_name):
        """Handle POST."""
        # TODO
        self.write({})

# -----------------------------------------------------------------------------


class FileNamesHandler(BaseMadDashHandler):
    """Handle querying list of filenames for given collection."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self, database_name, collection_name):
        """Handle GET."""
        collection = super().get_collection(database_name, collection_name)
        filelist = await collection.find_one({'name': 'filelist'})
        filenames = filelist['files']

        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenames})

# -----------------------------------------------------------------------------


def start(debug=False):
    """Start a Mad Dash DB service."""
    config = from_environment(EXPECTED_CONFIG)
    # logger = logging.getLogger('lta.rest')
    for name in config:
        logging.info(f"{name} = {config[name]}")

    args = RestHandlerSetup({
        'auth': {
            'secret': config['MAD_DASH_AUTH_SECRET'],
            'issuer': config['MAD_DASH_AUTH_ISSUER'],
            'algorithm': config['MAD_DASH_AUTH_ALGORITHM'],
        },
        'debug': debug
    })

    # configure access to MongoDB as a backing store
    mongo_user = quote_plus(config["MAD_DASH_MONGODB_AUTH_USER"])
    mongo_pass = quote_plus(config["MAD_DASH_MONGODB_AUTH_PASS"])
    mongo_host = config["MAD_DASH_MONGODB_HOST"]
    mongo_port = int(config["MAD_DASH_MONGODB_PORT"])
    # mongo_db = config["MAD_DASH_MONGODB_DATABASE_NAME"]
    # mongodb_url = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"
    mongodb_url = f"mongodb://{mongo_host}:{mongo_port}"
    if mongo_user and mongo_pass:
        # mongodb_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}"
        mongodb_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
    # ensure_mongo_indexes(mongodb_url, mongo_db)
    # motor_client = MotorClient(mongodb_url)
    # args['db_client'] = motor_client[mongo_db]
    args['db_client'] = MotorClient(mongodb_url)

    # configure REST routes
    server = RestServer(debug=debug)
    server.add_route(r'/$',
                     MainHandler, args)
    server.add_route(r'/databases$',
                     DatabasesHandler, args)  # get database names
    server.add_route(r'/(?P<database_name>\w+)/collections$',
                     CollectionsHandler, args)  # get collection names
    server.add_route(r'/(?P<database_name>\w+)/(?P<collection_name>[\w%-]+)/histograms$',
                     HistogramsHandler, args)  # get histogram names
    server.add_route(r'/(?P<database_name>\w+)/(?P<collection_name>[\w%-]+)/histogram/(?P<histogram_name>[\w%-]+)$',
                     HistogramObjectHandler, args)  # get histogram object
    server.add_route(r'/(?P<database_name>\w+)/(?P<collection_name>[\w%-]+)/files$',
                     FileNamesHandler, args)  # get file names

    server.startup(address=config['MAD_DASH_REST_HOST'], port=int(config['MAD_DASH_REST_PORT']))
    return server


def main():
    """Configure logging and start a Mad Dash DB service."""
    logging.basicConfig(level=logging.DEBUG)
    start(debug=True)
    loop = asyncio.get_event_loop()
    loop.run_forever()


if __name__ == '__main__':
    main()
