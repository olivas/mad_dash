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
        excludes = ['system.indexes', 'admin', 'local',
                    'simprod_filecatalog', 'config', 'token_service']
        database_names = [n for n in await self.db_client.list_database_names() if n not in excludes]

        self.write({'databases': database_names})

# -----------------------------------------------------------------------------


class CollectionsHandler(BaseMadDashHandler):
    """Handle querying list of collections from specified database."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_query_argument('database', default=None)

        database = super().get_database(database_name)
        collection_names = [n for n in await database.list_collection_names() if n != 'system.indexes']

        self.write({'database': database_name,
                    'collections': collection_names})

# -----------------------------------------------------------------------------


class HistogramsHandler(BaseMadDashHandler):
    """Handle querying list of histograms' names."""

    async def get_collection_contents(self, database_name, collection_name):
        """Return collection's contents."""
        collection = super().get_collection(database_name, collection_name)
        objs = []
        async for o in collection.find():
            objs.append(o)
        return objs

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_query_argument('database', default=None)
        collection_name = self.get_query_argument('collection', default=None)

        collection_contents = await self.get_collection_contents(database_name, collection_name)
        histogram_names = [d['name'] for d in collection_contents if d['name'] != 'filelist']

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histograms': histogram_names})

# -----------------------------------------------------------------------------


class HistogramObjectHandler(BaseMadDashHandler):
    """Handle querying/adding histogram object."""

    async def get_histogram(self, database_name, collection_name, histogram_name):
        """Return histogram object."""
        collection = super().get_collection(database_name, collection_name)
        try:
            histogram = await collection.find_one({'name': histogram_name})
        except StopIteration:
            raise tornado.web.HTTPError(400, reason=f"histogram not found ({histogram_name})")
        return histogram

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self, histogram_name):
        """Handle GET."""
        database_name = self.get_query_argument('database', default=None)
        collection_name = self.get_query_argument('collection', default=None)

        histogram = await self.get_histogram(database_name, collection_name, histogram_name)
        histogram = {k: histogram[k] for k in histogram if k != '_id'}

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': histogram})

    def get_create_collection(self, database_name, collection_name):
        """Return collection instance, if it doesn't exist, create it."""
        database = super().get_database(database_name)
        try:
            collection = database[collection_name]
        except KeyError:
            database.create_collection(collection_name)

        return collection

    def verify_histogram(self, database_name, collection_name, histogram):
        """Raise tornado errors if the histogram already exists or is not well structured."""
        schema = {'bin_values': list,
                  'name': str,
                  'underflow': int,
                  'xmax': int,
                  'xmin': int,
                  'overflow': int,
                  'nan_count': int}

        # check fields
        missing_keys = schema.keys() - set(histogram.keys())
        if missing_keys:
            raise tornado.web.HTTPError(400, reason=f"histogram has missing fields ({missing_keys})")
        extra_keys = set(histogram.keys()) - schema.keys()
        if extra_keys:
            raise tornado.web.HTTPError(400, reason=f"histogram has extra fields ({extra_keys})")

        # check types
        for field, _type in schema:
            if not isinstance(histogram[field], _type):
                raise tornado.web.HTTPError(400, reason=f"histogram field '{field}' is wrong type (should be {_type})")

        # check if histogram already exists
        exists = False
        try:
            exists = bool(await self.get_histogram(database_name, collection_name, histogram['name']))
        except tornado.web.HTTPError:
            return
        if exists:
            raise tornado.web.HTTPError(409, reason=f"histogram already in collection ({histogram['name']})")

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin'])
    async def post(self):
        """Handle POST."""
        database_name = self.get_query_argument('database', default=None)
        collection_name = self.get_query_argument('collection', default=None)
        histogram = self.get_query_argument('histogram', default=None)

        self.verify_histogram(database_name, collection_name, histogram)  # raises 400 or 409
        collection = self.get_create_collection(database_name, collection_name)

        # TODO
        self.write({})

# -----------------------------------------------------------------------------


class FileNamesHandler(BaseMadDashHandler):
    """Handle querying list of filenames for given collection."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['admin', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_query_argument('database', default=None)
        collection_name = self.get_query_argument('collection', default=None)

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
    server.add_route(r'/collections$',
                     CollectionsHandler, args)  # get collection names
    server.add_route(r'/histograms$',
                     HistogramsHandler, args)  # get histogram names
    server.add_route(r'/histograms/(?P<histogram_name>[\w%-]+)$',
                     HistogramObjectHandler, args)  # get histogram object
    server.add_route(r'/files$',
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
