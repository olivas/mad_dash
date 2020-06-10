"""Routes handlers for the Mad-Dash REST API server interface."""

import time
from typing import Any, List, Optional, Tuple, Union

import maddash_api as api
import tornado.web
from motor.motor_tornado import MotorClient, MotorCollection, MotorDatabase  # type: ignore
from rest_tools.client import json_decode  # type: ignore
from rest_tools.server import RestHandler, handler  # type: ignore

from .config import AUTH_PREFIX, EXCLUDE_DBS

REMOVE_ID = {"_id": False}

EXCLUDE_KEYS = ['_id', 'history']


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

    async def get_histogram_dicts_in_collection(self, database_name: str, collection_name: str) -> List[dict]:
        """Return collection's histogram dicts."""
        collection = self.get_collection(database_name, collection_name)

        objs = []
        async for o in collection.find(projection=REMOVE_ID):
            objs.append(o)

        return [d for d in objs if d['name'] != 'filelist']


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

        histo_dicts = await self.md_mc.get_histogram_dicts_in_collection(database_name, collection_name)
        histogram_names = [c['name'] for c in histo_dicts]

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

        histo_dicts = await self.md_mc.get_histogram_dicts_in_collection(database_name, collection_name)

        self.write({'database': database_name,
                    'collection': collection_name,
                    'histograms': histo_dicts})


# -----------------------------------------------------------------------------


class HistogramHandler(BaseMadDashHandler):
    """Handle querying/adding histogram object."""

    async def get_histogram(self, database_name: str, collection_name: str, histogram_name: str, remove_id: bool=True) -> Optional[api.Histogram]:
        """Return histogram object."""
        collection = self.md_mc.get_collection(database_name, collection_name)

        if remove_id:
            histogram_dict = await collection.find_one({'name': histogram_name}, projection=REMOVE_ID)
        else:
            histogram_dict = await collection.find_one({'name': histogram_name})

        if not histogram_dict:
            return None

        histogram = api.Histogram.from_dict(histogram_dict)
        return histogram

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
                    'histogram': histogram.to_dict(exclude=EXCLUDE_KEYS),
                    'history': histogram.history})

    async def update_histogram(self, database_name: str, collection_name: str, histogram: api.Histogram) -> None:
        """Update the histogram's values. Assumes the histogram already exits.

        Write back to output buffer.
        """
        db_histo = await self.get_histogram(database_name, collection_name,
                                            histogram.name, remove_id=False)
        if not db_histo:  # here to appease mypy
            raise Exception("There is no histogram to update. This should've been caught upstream.")

        db_histo.update(histogram)

        # put in DB
        collection = self.md_mc.get_collection(database_name, collection_name)
        histo_dict = db_histo.to_dict()
        result = await collection.replace_one({'_id': histo_dict['_id']}, histo_dict)

        # write
        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': db_histo.to_dict(exclude=EXCLUDE_KEYS),
                    'history': db_histo.history,
                    'updated': result.acknowledged})

    async def insert_histogram(self, database_name: str, collection_name: str, histogram: api.Histogram) -> None:
        """Insert the novel histogram.

        Write back to output buffer.
        """
        histogram.add_to_history()  # record when this happened

        # put in DB
        collection = await self.md_mc.get_create_collection(database_name, collection_name)
        await collection.insert_one(histogram.to_dict())

        # write
        self.write({'database': database_name,
                    'collection': collection_name,
                    'histogram': histogram.to_dict(exclude=EXCLUDE_KEYS),
                    'history': histogram.history,
                    'updated': False})

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production'])
    async def post(self) -> None:
        """Handle POST."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')
        histogram_dict = self.get_required_argument('histogram')
        update = self.get_optional_argument('update', default=False)

        # check reserved key(s)
        if 'history' in histogram_dict:
            raise tornado.web.HTTPError(400, reason="histogram cannot define the field 'history'")

        # check type and structure
        try:
            histogram = api.Histogram.from_dict(histogram_dict)
        except (AttributeError, TypeError, NameError) as e:
            raise tornado.web.HTTPError(400, reason=str(e))

        # is the histogram already in the collection?
        async def histogram_exists() -> bool:
            return bool(await self.get_histogram(database_name, collection_name, histogram.name))

        # update/insert
        if await histogram_exists():
            if not update:
                raise tornado.web.HTTPError(409, reason=f"histogram already in collection ({histogram.name})")
            await self.update_histogram(database_name, collection_name, histogram)
        else:
            await self.insert_histogram(database_name, collection_name, histogram)


# -----------------------------------------------------------------------------


class FileNamesHandler(BaseMadDashHandler):
    """Handle querying list of filenames for given collection."""

    async def get_filelist_attributes(self, database_name: str, collection_name: str, remove_id: bool=True) -> Tuple[Any, List[str], List[Union[int, float]]]:
        """Return filelist-dict's id, filenames, and history in collection.

        Raise {TypeError} if filelist-dict not in collection.
        """
        collection = self.md_mc.get_collection(database_name, collection_name)

        if remove_id:
            dict_ = await collection.find_one({'name': 'filelist'}, projection=REMOVE_ID)
        dict_ = await collection.find_one({'name': 'filelist'})

        history = []  # type: List[Union[int,float]]
        if 'history' in dict_:  # old collections may not have a history defined
            history = dict_['history']

        return dict_['_id'], dict_['files'], history

    @handler.scope_role_auth(prefix=AUTH_PREFIX, roles=['production', 'web'])
    async def get(self) -> None:
        """Handle GET."""
        database_name = self.get_required_argument('database')
        collection_name = self.get_required_argument('collection')

        try:
            _, filenames, history = await self.get_filelist_attributes(database_name, collection_name)
        except TypeError:
            filenames = []
            history = []

        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenames,
                    'history': history})

    async def update_filelist(self, database_name: str, collection_name: str, new_filenames: List[str]) -> None:
        """Update (extends) filelist. Assumes the filelist already exits.

        Write back to output buffer.
        """
        _id, prev_filenames, history = await self.get_filelist_attributes(database_name, collection_name, remove_id=False)

        filenames = sorted(set(new_filenames) | set(prev_filenames))

        if not history:
            history = [0.0]  # must be an old filelist, so it didn't come with a history
        history.append(time.time())

        # put in DB
        collection = self.md_mc.get_collection(database_name, collection_name)
        dict_ = {'name': 'filelist',
                 'files': filenames,
                 'history': history}
        result = await collection.replace_one({'_id': _id}, dict_)

        # write
        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenames,
                    'history': history,
                    'updated': result.acknowledged})

    async def insert_filelist(self, database_name: str, collection_name: str, filenames: List[str]) -> None:
        """Insert novel filelist object.

        Write back to output buffer.
        """
        collection = await self.md_mc.get_create_collection(database_name, collection_name)
        history = [time.time()]

        # put in DB
        await collection.insert_one({'name': 'filelist',
                                     'files': filenames,
                                     'history': history})

        # write
        self.write({'database': database_name,
                    'collection': collection_name,
                    'files': filenames,
                    'history': history,
                    'updated': False})

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

        # is the filelist already in the collection?
        async def filelist_exists() -> bool:
            try:
                await self.get_filelist_attributes(database_name, collection_name)
                return True
            except TypeError:
                return False

        # update/insert
        if await filelist_exists():
            if not update:
                raise tornado.web.HTTPError(409, reason=f"files already in collection, {collection_name}")
            await self.update_filelist(database_name, collection_name, filenamelist)
        else:
            await self.insert_filelist(database_name, collection_name, filenamelist)


# -----------------------------------------------------------------------------
