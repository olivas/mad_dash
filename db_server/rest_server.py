"""Mad-Dash REST API server interface."""

import asyncio
import logging
from urllib.parse import quote_plus

import tornado.web
from motor.motor_tornado import MotorClient
from rest_tools.client import json_decode
from rest_tools.server import RestHandler, RestHandlerSetup, RestServer, from_environment, handler

AUTH_PREFIX = "maddash"

EXPECTED_CONFIG = {
    'MAD_DASH_AUTH_ALGORITHM': 'HS512',  # 'RS256',
    'MAD_DASH_AUTH_ISSUER': 'http://localhost:8888',  # 'maddash',
    'MAD_DASH_AUTH_SECRET': 'secret',
    'MAD_DASH_MONGODB_AUTH_USER': '',  # None means required to specify
    'MAD_DASH_MONGODB_AUTH_PASS': '',  # empty means no authentication required
    'MAD_DASH_MONGODB_HOST': 'localhost',
    'MAD_DASH_MONGODB_PORT': '27017',
    'MAD_DASH_REST_HOST': 'localhost',
    'MAD_DASH_REST_PORT': '8080',
}

EXCLUDE_DBS = ['system.indexes', 'production', 'local',
               'simprod_filecatalog', 'config', 'token_service', 'admin']

REMOVE_ID = {"_id": False}

# -----------------------------------------------------------------------------


class MadDashMotorClient():
    """MotorClient with additional guardrails for Mad-Dash things."""

    def __init__(self, motor_client):
        """Set-up."""
        self.motor_client = motor_client

    async def get_database_names(self):
        """Return all databases' names."""
        database_names = [n for n in await self.motor_client.list_database_names() if n not in EXCLUDE_DBS]
        return database_names

    def get_database(self, database_name):
        """Return database instance."""
        try:
            return self.motor_client[database_name]
        except (KeyError, TypeError):
            raise tornado.web.HTTPError(400, reason=f"database not found ({database_name})")

    async def get_collection_names(self, database_name):
        """Return collection names in database."""
        database = self.get_database(database_name)
        collection_names = [n for n in await database.list_collection_names() if n != 'system.indexes']

        return collection_names

    def get_collection(self, database_name, collection_name):
        """Return collection instance."""
        database = self.get_database(database_name)
        try:
            return database[collection_name]
        except KeyError:
            raise tornado.web.HTTPError(400, reason=f"collection not found ({collection_name})")

    async def ensure_collection_indexes(self, database_name, collection_name):
        """Create indexes in collection."""
        collection = self.get_collection(database_name, collection_name)
        await collection.create_index('name', name='name_index', unique=True)
        async for index in collection.list_indexes():
            print(index)

    async def ensure_all_databases_indexes(self):
        """Create all indexes in all databases."""
        for database_name in await self.get_database_names():
            for collection_name in await self.get_collection_names(database_name):
                await self.ensure_collection_indexes(database_name, collection_name)

    async def get_create_collection(self, database_name, collection_name):
        """Return collection instance, if it doesn't exist, create it."""
        database = self.get_database(database_name)
        try:
            collection = database[collection_name]
        except KeyError:
            database.create_collection(collection_name)
            await self.ensure_collection_indexes(database_name, collection_name)

        return collection

    async def get_histograms_in_collection(self, database_name, collection_name):
        """Return collection's contents."""
        collection = self.get_collection(database_name, collection_name)

        objs = []
        async for o in collection.find(projection=REMOVE_ID):
            objs.append(o)

        return [c for c in objs if c['name'] != 'filelist']

# -----------------------------------------------------------------------------


class BaseMadDashHandler(RestHandler):
    """BaseMadDashHandler is a RestHandler for all Mad-Dash routes."""

    def initialize(self, motor_client, *args, **kwargs):  # pylint: disable=W0221
        """Initialize a BaseMadDashHandler object."""
        super(BaseMadDashHandler, self).initialize(*args, **kwargs)
        # self.motor_client = motor_client  # pylint: disable=W0201
        self.md_mc = MadDashMotorClient(motor_client)  # pylint: disable=W0201

    def get_optional_argument(self, name, default=None):
        """Return argument, or default value if not present."""
        try:
            return self.get_required_argument(name)
        except tornado.web.HTTPError:
            return default

    def get_required_argument(self, name):
        """Return argument, raise 400 if not present."""
        if self.request.body:
            try:
                return json_decode(self.request.body)[name]
            except KeyError:
                pass
        try:
            return self.get_query_argument(name)
        except tornado.web.MissingArgumentError:
            pass
        # fall-through
        raise tornado.web.HTTPError(400, reason=f"missing argument ({name})")


# -----------------------------------------------------------------------------


class MainHandler(BaseMadDashHandler):
    """MainHandler is a BaseMadDashHandler that handles the root route."""

    def get(self):
        """Handle GET."""
        self.write({})

# -----------------------------------------------------------------------------


class DatabasesNamesHandler(BaseMadDashHandler):
    """Handle querying list of databases in mongodb client."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self):
        """Handle GET."""
        database_names = await self.md_mc.get_database_names()

        self.write({'databases': database_names})

# -----------------------------------------------------------------------------


class CollectionsNamesHandler(BaseMadDashHandler):
    """Handle querying list of collections from specified database."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_required_argument('database')

        collection_names = await self.md_mc.get_collection_names(database_name)

        self.write({'database': database_name,
                    'collections': collection_names})

# -----------------------------------------------------------------------------


class CollectionsHistogramsNamesHandler(BaseMadDashHandler):
    """Handle querying list of histograms' names."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')

        histograms = await self.md_mc.get_histograms_in_collection(database_name, collection_name)
        histogram_names = [c['name'] for c in histograms]

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histograms': histogram_names})

# -----------------------------------------------------------------------------


class CollectionsHistogramsHandler(BaseMadDashHandler):
    """Handle querying list of histogram objects in given collection."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')

        histograms = await self.md_mc.get_histograms_in_collection(database_name, collection_name)

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histograms': histograms})

# -----------------------------------------------------------------------------


class HistogramHandler(BaseMadDashHandler):
    """Handle querying/adding histogram object."""

    async def get_histogram(self, database_name, collection_name, histogram_name, remove_id=True):
        """Return histogram object."""
        collection = self.md_mc.get_collection(database_name, collection_name)

        if remove_id:
            histogram = await collection.find_one({'name': histogram_name}, projection=REMOVE_ID)
        else:
            histogram = await collection.find_one({'name': histogram_name})

        return histogram

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')
        histogram_name = self.get_required_argument('name')

        histogram = await self.get_histogram(database_name, collection_name, histogram_name)
        if not histogram:
            raise tornado.web.HTTPError(400, reason=f"histogram not found ({histogram_name})")

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': histogram})

    @staticmethod
    def verify_histogram_schema(histogram):
        """Raise tornado errors if the histogram already exists or is not well structured."""
        schema = {'name': str,
                  'xmax': int,
                  'xmin': int,
                  'overflow': int,
                  'underflow': int,
                  'nan_count': int,
                  'bin_values': list}

        # check fields
        missing_keys = schema.keys() - set(histogram.keys())
        if missing_keys:
            raise tornado.web.HTTPError(400, reason=f"histogram has missing fields ({missing_keys})")

        # check types
        for field, _type in schema.items():
            if not isinstance(histogram[field], _type):
                raise tornado.web.HTTPError(400, reason=f"histogram field '{field}' is wrong type (should be {_type})")

        if histogram['name'] == 'filelist':
            raise tornado.web.HTTPError(400, reason="histogram cannot be named 'filelist'")

    async def histogram_exists(self, database_name, collection_name, histogram_name):
        """Return whether histogram already exists."""
        exists = bool(await self.get_histogram(database_name, collection_name, histogram_name))
        return exists

    async def update_histogram(self, database_name, collection_name, histogram):
        """Update the histogram's values. Assumes the histogram already exits."""
        prev_histo = await self.get_histogram(database_name, collection_name,
                                              histogram['name'], remove_id=False)

        bin_values = [b1 + b2 for b1, b2 in zip(histogram['bin_values'], prev_histo['bin_values'])]
        histogram['bin_values'] = bin_values
        histogram['overflow'] += prev_histo['overflow']
        histogram['underflow'] += prev_histo['underflow']
        histogram['nan_count'] += prev_histo['nan_count']

        collection = self.md_mc.get_collection(database_name, collection_name)
        result = await collection.replace_one({'_id': prev_histo['_id']}, histogram)

        return result.acknowledged

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production'])
    async def post(self):
        """Handle POST."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')
        histogram = self.get_required_argument('histogram')
        update = self.get_optional_argument('update', default=False)

        # raise 400
        HistogramHandler.verify_histogram_schema(histogram)

        # update/insert
        histo_updated = False
        if await self.histogram_exists(database_name, collection_name, histogram['name']):
            if not update:
                raise tornado.web.HTTPError(409, reason=f"histogram already in collection ({histogram['name']})")
            histo_updated = await self.update_histogram(database_name, collection_name, histogram)
        else:
            collection = await self.md_mc.get_create_collection(database_name, collection_name)
            await collection.insert_one(histogram)

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': {k: histogram[k] for k in histogram if k != '_id'},
                    'updated': histo_updated})

# -----------------------------------------------------------------------------


class FileNamesHandler(BaseMadDashHandler):
    """Handle querying list of filenames for given collection."""

    async def get_filelist(self, database_name, collection_name, remove_id=True):
        """Return list of files in collection."""
        collection = self.md_mc.get_collection(database_name, collection_name)

        if remove_id:
            return await collection.find_one({'name': 'filelist'}, projection=REMOVE_ID)
        return await collection.find_one({'name': 'filelist'})

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self):
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')

        filenamelist = []
        filelist = await self.get_filelist(database_name, collection_name)
        if filelist:
            filenamelist = filelist['files']

        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenamelist})

    async def update_filelist(self, database_name, collection_name, filenamelist):
        """Update (extends) filelist. Assumes the filelist already exits."""
        prev_filelist = await self.get_filelist(database_name, collection_name, remove_id=False)

        filenamelist = sorted(set(filenamelist) | set(prev_filelist['files']))

        collection = self.md_mc.get_collection(database_name, collection_name)
        filelist = {'name': 'filelist',
                    'files': filenamelist}
        result = await collection.replace_one({'_id': prev_filelist['_id']}, filelist)

        return result.acknowledged, filenamelist

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production'])
    async def post(self):
        """Handle POST."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')
        filenamelist = self.get_required_argument('files')
        update = self.get_optional_argument('update', default=False)

        # type check
        if not isinstance(filenamelist, list):
            raise tornado.web.HTTPError(400, reason=f"'files' field is not a list ({type(filenamelist)})")

        # update/insert
        files_updated = False
        if await self.get_filelist(database_name, collection_name):
            if not update:
                raise tornado.web.HTTPError(409, reason=f"files already in collection, {collection_name}")
            files_updated, filenamelist = await self.update_filelist(database_name, collection_name, filenamelist)
        else:
            collection = await self.md_mc.get_create_collection(database_name, collection_name)
            await collection.insert_one({'name': 'filelist',
                                         'files': filenamelist})

        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenamelist,
                    'updated': files_updated})


# -----------------------------------------------------------------------------


def start(debug=False):
    """Start a Mad Dash REST service."""
    config = from_environment(EXPECTED_CONFIG)

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
    mongodb_url = f"mongodb://{mongo_host}:{mongo_port}"
    if mongo_user and mongo_pass:
        mongodb_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"

    # ensure indexes
    md_mc = MadDashMotorClient(MotorClient(mongodb_url))
    asyncio.get_event_loop().run_until_complete(md_mc.ensure_all_databases_indexes())

    args['motor_client'] = MotorClient(mongodb_url)

    # configure REST routes
    server = RestServer(debug=debug)
    server.add_route(r'/$',
                     MainHandler, args)
    server.add_route(r'/databases/names$',
                     DatabasesNamesHandler, args)  # get database names
    server.add_route(r'/collections/names$',
                     CollectionsNamesHandler, args)  # get collection names
    server.add_route(r'/collections/histograms/names$',
                     CollectionsHistogramsNamesHandler, args)  # get all histogram names in collection
    server.add_route(r'/collections/histograms$',
                     CollectionsHistogramsHandler, args)  # get all histogram objects in collection
    server.add_route(r'/histogram$',
                     HistogramHandler, args)  # get histogram object
    server.add_route(r'/files/names$',
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
