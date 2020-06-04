"""Routes handlers for the Mad-Dash REST API server interface."""

import time
from typing import Any, Dict, List, Tuple, Union

import tornado.web
from motor.motor_tornado import MotorClient, MotorCollection, MotorDatabase  # type: ignore
from rest_tools.client import json_decode  # type: ignore
from rest_tools.server import RestHandler, handler  # type: ignore

from .config import AUTH_PREFIX, EXCLUDE_DBS

REMOVE_ID = {"_id": False}


# -----------------------------------------------------------------------------


class MadDashMotorClient():
    """MotorClient with additional guardrails for Mad-Dash things."""

    def __init__(self, motor_client: MotorClient) -> None:
        """Init."""
        self.motor_client = motor_client

    async def get_database_names(self) -> List[str]:
        """Return all databases' names."""
        database_names = [n for n in await self.motor_client.list_database_names() if n not in EXCLUDE_DBS]
        return database_names

    def get_database(self, database_name: str) -> MotorDatabase:
        """Return database instance."""
        try:
            return self.motor_client[database_name]
        except (KeyError, TypeError):
            raise tornado.web.HTTPError(400, reason=f"database not found ({database_name})")

    async def get_collection_names(self, database_name: str) -> List[str]:
        """Return collection names in database."""
        database = self.get_database(database_name)
        collection_names = [n for n in await database.list_collection_names() if n != 'system.indexes']

        return collection_names

    def get_collection(self, database_name: str, collection_name: str) -> MotorCollection:
        """Return collection instance."""
        database = self.get_database(database_name)
        try:
            return database[collection_name]
        except KeyError:
            raise tornado.web.HTTPError(400, reason=f"collection not found ({collection_name})")

    async def ensure_collection_indexes(self, database_name: str, collection_name: str) -> None:
        """Create indexes in collection."""
        collection = self.get_collection(database_name, collection_name)
        await collection.create_index('name', name='name_index', unique=True)
        async for index in collection.list_indexes():
            print(index)

    async def ensure_all_databases_indexes(self) -> None:
        """Create all indexes in all databases."""
        for database_name in await self.get_database_names():
            for collection_name in await self.get_collection_names(database_name):
                await self.ensure_collection_indexes(database_name, collection_name)

    async def get_create_collection(self, database_name: str, collection_name: str) -> MotorCollection:
        """Return collection instance, if it doesn't exist, create it."""
        database = self.get_database(database_name)
        try:
            collection = database[collection_name]
        except KeyError:
            database.create_collection(collection_name)
            await self.ensure_collection_indexes(database_name, collection_name)

        return collection

    async def get_histograms_in_collection(self, database_name: str, collection_name: str) -> List[dict]:
        """Return collection's contents."""
        collection = self.get_collection(database_name, collection_name)

        objs = []
        async for o in collection.find(projection=REMOVE_ID):
            objs.append(o)

        return [c for c in objs if c['name'] != 'filelist']


# -----------------------------------------------------------------------------


class BaseMadDashHandler(RestHandler):
    """BaseMadDashHandler is a RestHandler for all Mad-Dash routes."""

    def initialize(self, motor_client: MotorClient, *args, **kwargs) -> None:  # pylint: disable=W0221
        """Initialize a BaseMadDashHandler object."""
        super(BaseMadDashHandler, self).initialize(*args, **kwargs)
        # self.motor_client = motor_client  # pylint: disable=W0201
        self.md_mc = MadDashMotorClient(motor_client)  # pylint: disable=W0201

    def get_optional_argument(self, name: str, default: Any = None) -> Any:
        """Return argument, or default value if not present."""
        try:
            return self.get_required_argument(name)
        except tornado.web.HTTPError:
            return default

    def get_required_argument(self, name: str) -> Any:
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

    def get(self) -> None:
        """Handle GET."""
        self.write({})


# -----------------------------------------------------------------------------


class DatabasesNamesHandler(BaseMadDashHandler):
    """Handle querying list of databases in mongodb client."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self) -> None:
        """Handle GET."""
        database_names = await self.md_mc.get_database_names()

        self.write({'databases': database_names})


# -----------------------------------------------------------------------------


class CollectionsNamesHandler(BaseMadDashHandler):
    """Handle querying list of collections from specified database."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self) -> None:
        """Handle GET."""
        database_name = self.get_required_argument('database')

        collection_names = await self.md_mc.get_collection_names(database_name)

        self.write({'database': database_name,
                    'collections': collection_names})


# -----------------------------------------------------------------------------


class CollectionsHistogramsNamesHandler(BaseMadDashHandler):
    """Handle querying list of histograms' names."""

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self) -> None:
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
    async def get(self) -> None:
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

    async def get_histogram(self, database_name: str, collection_name: str, histogram_name: str, remove_id: bool=True) -> dict:
        """Return histogram object."""
        collection = self.md_mc.get_collection(database_name, collection_name)

        if remove_id:
            histogram = await collection.find_one({'name': histogram_name}, projection=REMOVE_ID)
        else:
            histogram = await collection.find_one({'name': histogram_name})

        return histogram

    @staticmethod
    def _histogram_with_good_fields(histogram: dict) -> dict:
        return {k: histogram[k] for k in histogram if k not in ['_id', 'history']}

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self) -> None:
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')
        histogram_name = self.get_required_argument('name')

        histogram = await self.get_histogram(database_name, collection_name, histogram_name)
        if not histogram:
            raise tornado.web.HTTPError(400, reason=f"histogram not found ({histogram_name})")

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': HistogramHandler._histogram_with_good_fields(histogram),
                    'history': histogram['history']})

    @staticmethod
    def verify_histogram_schema(histogram: dict) -> None:
        """Raise tornado errors if the histogram already exists or is not well structured."""
        schema = {'name': str,
                  'xmax': (int, float),
                  'xmin': (int, float),
                  'overflow': int,
                  'underflow': int,
                  'nan_count': int,
                  'bin_values': list}  # type: Dict[str, Union[type, Tuple[type, ...]]]

        # check fields
        missing_keys = schema.keys() - set(histogram.keys())
        if missing_keys:
            raise tornado.web.HTTPError(400, reason=f"histogram has missing fields ({missing_keys})")

        # check types
        for field, _type in schema.items():
            if not isinstance(histogram[field], _type):
                raise tornado.web.HTTPError(400, reason=f"histogram field '{field}' is wrong type (should be {_type})")

        # check for illegal names/keys
        if histogram['name'] == 'filelist':
            raise tornado.web.HTTPError(400, reason="histogram cannot be named 'filelist'")
        if 'history' in histogram:
            raise tornado.web.HTTPError(400, reason="histogram cannot define the field 'history'")

    async def histogram_exists(self, database_name: str, collection_name: str, histogram_name: str) -> bool:
        """Return whether histogram already exists."""
        exists = bool(await self.get_histogram(database_name, collection_name, histogram_name))
        return exists

    async def update_histogram(self, database_name: str, collection_name: str, histogram: dict) -> bool:
        """Update the histogram's values. Assumes the histogram already exits."""
        prev_histo = await self.get_histogram(database_name, collection_name,
                                              histogram['name'], remove_id=False)

        bin_values = [b1 + b2 for b1, b2 in zip(histogram['bin_values'], prev_histo['bin_values'])]
        histogram['bin_values'] = bin_values
        histogram['overflow'] += prev_histo['overflow']
        histogram['underflow'] += prev_histo['underflow']
        histogram['nan_count'] += prev_histo['nan_count']

        # record when this happened
        if 'history' not in histogram:
            histogram['history'] = [0.0]  # must be old histogram, so it didn't come with a history
        histogram['history'].append(time.time())

        # put in DB
        collection = self.md_mc.get_collection(database_name, collection_name)
        result = await collection.replace_one({'_id': prev_histo['_id']}, histogram)

        return result.acknowledged

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production'])
    async def post(self) -> None:
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
            histogram['history'] = [time.time()]  # record when this happened
            await collection.insert_one(histogram)

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': HistogramHandler._histogram_with_good_fields(histogram),
                    'history': histogram['history'],
                    'updated': histo_updated})


# -----------------------------------------------------------------------------


class FileNamesHandler(BaseMadDashHandler):
    """Handle querying list of filenames for given collection."""

    async def get_filelist(self, database_name: str, collection_name: str, remove_id: bool=True) -> Dict[str, list]:
        """Return list of files in collection."""
        collection = self.md_mc.get_collection(database_name, collection_name)

        if remove_id:
            return await collection.find_one({'name': 'filelist'}, projection=REMOVE_ID)
        return await collection.find_one({'name': 'filelist'})

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self) -> None:
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')

        filenamelist = []  # type: List[str]
        history = []  # type: List[float]
        filelist = await self.get_filelist(database_name, collection_name)
        if filelist:
            filenamelist = filelist['files']
            history = filelist['history']

        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenamelist,
                    'history': history})

    async def update_filelist(self, database_name: str, collection_name: str, filenamelist: List[str]) -> Tuple[bool, List[str], List[float]]:
        """Update (extends) filelist. Assumes the filelist already exits."""
        prev_filelist = await self.get_filelist(database_name, collection_name, remove_id=False)

        filenamelist = sorted(set(filenamelist) | set(prev_filelist['files']))

        if 'history' not in prev_filelist:
            history = [0.0]  # must be an old filelist, so it didn't come with a history
        else:
            history = prev_filelist['history']
        history.append(time.time())

        collection = self.md_mc.get_collection(database_name, collection_name)
        filelist = {'name': 'filelist',
                    'files': filenamelist,
                    'history': history}
        result = await collection.replace_one({'_id': prev_filelist['_id']}, filelist)

        return result.acknowledged, filenamelist, history

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production'])
    async def post(self) -> None:
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
            files_updated, filenamelist, history = await self.update_filelist(database_name, collection_name, filenamelist)
        else:
            collection = await self.md_mc.get_create_collection(database_name, collection_name)
            history = [time.time()]
            await collection.insert_one({'name': 'filelist',
                                         'files': filenamelist,
                                         'history': history})

        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenamelist,
                    'history': history,
                    'updated': files_updated})


# -----------------------------------------------------------------------------
