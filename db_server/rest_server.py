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
    'MAD_DASH_AUTH_ALGORITHM': 'RS256',
    'MAD_DASH_AUTH_ISSUER': 'maddash',
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
            raise tornado.web.HTTPError(400, reason="bad request (bad database name)")

    def get_collection(self, database_name, collection_name):
        """Return collection instance."""
        database = self.get_database(database_name)
        try:
            return database[collection_name]
        except KeyError:
            raise tornado.web.HTTPError(400, reason="bad request (bad collection_name name)")

# -----------------------------------------------------------------------------


class MainHandler(BaseMadDashHandler):
    """MainHandler is a BaseMadDashHandler that handles the root route."""

    def get(self):
        """Handle GET."""
        self.write({})

# -----------------------------------------------------------------------------


class DatabasesHandler(BaseMadDashHandler):
    """ """

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['web'])
    async def get(self):
        """Handle GET."""
        excludes = ('system.indexes', 'admin', 'local', 'simprod_filecatalog')
        database_names = [n for n in self.db_client.database_names() if n not in excludes]

        self.write({'databases': database_names})

# -----------------------------------------------------------------------------


class CollectionsHandler(BaseMadDashHandler):
    """ """

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['web'])
    async def get(self, database_name):
        """Handle GET."""
        database = super().get_database(database_name)
        collection_names = [n for n in database.collection_names() if n != 'system.indexes']

        self.write({'collections': collection_names})

# -----------------------------------------------------------------------------


class HistogramsHandler(BaseMadDashHandler):
    """ """

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['web'])
    async def get(self, database_name, collection_name):
        """Handle GET."""
        collection = super().get_collection(database_name, collection_name)
        histogram_names = [d['name'] for d in collection.find() if d['name'] != 'filelist']

        self.write({'histograms': histogram_names})

# -----------------------------------------------------------------------------


class HistogramObjectsHandler(BaseMadDashHandler):
    """ """

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['web'])
    async def get(self, database_name, collection_name):
        """Handle GET."""
        collection = super().get_collection(database_name, collection_name)
        histograms = [d for d in collection.find() if d['name'] != 'filelist']

        self.write({'histograms': histograms})

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['iceprod'])
    async def post(self, database_name, collection_name):
        """Handle POST."""
        req = json_decode(self.request.body)
        # TODO
        self.write({})

# -----------------------------------------------------------------------------


class FileNamesHandler(BaseMadDashHandler):
    """ """

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['web'])
    async def get(self, database_name, collection_name):
        """Handle GET."""
        collection = super().get_collection(collection_name, database_name)
        filelist = collection.find_one({'name': 'filelist'})['files']

        self.write({'files': filelist})

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
    server.add_route(r'/',
                     MainHandler, args)
    server.add_route(r'/database/names',
                     DatabasesHandler, args)  # get database names
    server.add_route(r'/(?P<database_name>\w+)/collections',
                     CollectionsHandler, args)  # get collection names; in: None; out [""]
    server.add_route(r'/(?P<database_name>\w+)/(?P<collection_name>\w+)/histograms',
                     HistogramsHandler, args)  # get histogram names; in: None; out []
    server.add_route(r'/(?P<database_name>\w+)/(?P<collection_name>\w+)/histograms/objects',
                     HistogramObjectsHandler, args)  # get histogram object(s); input [{}]
    server.add_route(r'/(?P<database_name>\w+)/(?P<collection_name>\w+)/files',
                     FileNamesHandler, args)  # get histogram names; in: None

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
