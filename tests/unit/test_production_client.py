"""Test production client."""

import copy
import os
import pickle
from typing import Any, Dict

# local imports
from production_client import ingest_pickled_collections
from production_client.ingest_pickled_collections import Collection


class TestIngestPickledCollections:
    """Test ingest_pickled_collections.py."""

    COLLECTION = {
        'LineFitEnergy': {
            'bin_values': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'name': 'LineFitEnergy',
            'underflow': 0,
            'xmax': 10.0,
            'xmin': 0.0,
            'overflow': 0,
            'expression': "log10(frame['LineFit'].energy)",
            'nan_count': 38869
        },
        'OnlineL2_SplineMPESpeed': {
            'bin_values': [0, 0, 0, 0, 0],
            'name': 'OnlineL2_SplineMPESpeed',
            'underflow': 0,
            'xmax': 10.0,
            'xmin': 0.0,
            'overflow': 0,
            'expression': "(frame['OnlineL2_SplineMPE'].speed)",
            'nan_count': 0
        },
        'filelist': {
            'files': ['test_one.i3.zst', 'test_two.i3.zst', 'test_three.i3.zst']
        }
    }  # type: Collection

    @staticmethod
    def make_pickle(collection_name: str, dict_: Dict[str, Any]) -> str:
        """Pickle collection dict and return filepath."""
        filename = f'{collection_name}.pkl'
        pickle.dump(dict_, open(filename, 'wb'))
        return os.path.abspath(filename)

    @staticmethod
    def delete_pickle(filename: str) -> None:
        """Delete `filename`."""
        os.remove(filename)

    @staticmethod
    def test_10() -> None:
        """Test get_each_collection()."""
        collection_name = 'TEST_10_COLLECTION'
        collection_dict = TestIngestPickledCollections.COLLECTION
        filename = TestIngestPickledCollections.make_pickle(collection_name, collection_dict)
        print(filename)

        paths = [filename]
        for collection, name in ingest_pickled_collections.get_each_collection(paths):
            assert collection == collection_dict
            assert name == collection_name

        TestIngestPickledCollections.delete_pickle(filename)

    @staticmethod
    def test_20() -> None:
        """Test get_each_histogram()."""
        collection = copy.deepcopy(TestIngestPickledCollections.COLLECTION)

        collection_name = 'TEST_20_COLLECTION'
        for h in ingest_pickled_collections.get_each_histogram(collection, collection_name):
            assert h['name'] in collection
            assert h == collection[h['name']]

    @staticmethod
    def test_30() -> None:
        """Test get_each_histogram()."""
        collection = TestIngestPickledCollections.COLLECTION

        collection_name = 'TEST_30_COLLECTION'
        filelist = ingest_pickled_collections.get_filelist(collection, collection_name)
        assert filelist == collection['filelist']['files']
