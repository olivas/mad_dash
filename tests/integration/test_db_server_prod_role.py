"""Integration test the production client."""

# pylint: disable=redefined-outer-name

import copy
import uuid
from typing import Any, Dict, List

import pytest  # type: ignore
import requests

# local imports
from rest_tools.client import RestClient  # type: ignore

# types
Histogram = Dict[str, Any]


@pytest.fixture  # type: ignore
def db_rc() -> RestClient:
    """Get database REST client."""
    token_json = requests.get(
        "http://localhost:8888/token?scope=maddash:production"
    ).json()
    rc = RestClient(
        "http://localhost:8080", token=token_json["access"], timeout=5, retries=0
    )
    return rc


HISTOGRAMS = [
    {
        # fmt: off
        'bin_values': [9, 9, 15, 8, 10, 18, 18, 25, 26, 28, 36, 35, 36, 34, 42, 33, 28,
                       37, 30, 41, 27, 21, 22, 33, 41, 32, 34, 36, 37, 36, 36, 38, 32,
                       32, 36, 40, 29, 40, 42, 35, 46, 38, 41, 37, 50, 41, 52, 67, 70,
                       58, 70, 86, 95, 94, 161, 174, 201, 154, 171, 190, 268, 343, 436,
                       453, 462, 416, 395, 301, 230, 200, 159, 113, 80, 74, 57, 41, 47,
                       46, 42, 48, 38, 39, 39, 34, 37, 37, 24, 35, 30, 20, 29, 21, 23,
                       31, 31, 30, 24, 34, 25, 37],
        # fmt: on
        "name": "OnlineL2_SplineMPE_TruncatedEnergy_DOMS_MuonCosZenith",
        "underflow": 1,
        "xmax": 1,
        "xmin": -1,
        "overflow": 2,
        "expression": "cos(frame['OnlineL2_SplineMPE_TruncatedEnergy_DOMS_Muon'].dir.zenith)",
        "nan_count": 3,
    },
    {
        # fmt: off
        'bin_values': [133, 97, 41, 194, 240, 49, 229, 230, 200, 54, 138, 106, 262, 276,
                       87, 125, 89, 78, 216, 205, 277, 206, 211, 223, 249, 138, 50, 218,
                       233, 104, 296, 170, 219, 298, 77, 89, 155, 277, 200, 282, 64,
                       196, 251, 252, 55, 89, 70, 283, 138, 14, 138, 206, 116, 196, 45,
                       161, 107, 131, 152, 186, 85, 178, 96, 54, 130, 221, 291, 63, 34,
                       89, 215, 135, 84, 117, 268, 206, 19, 179, 279, 9, 142, 241, 282,
                       209, 11, 236, 232, 77, 250, 299, 43, 133, 91, 262, 65, 220, 243,
                       133],
        # fmt: on
        "name": "TestMade_UpData",
        "underflow": -3,
        "xmax": 10,
        "xmin": -17,
        "overflow": 0,
        "nan_count": 4,
    },
]


class TestDBServerProdRole:
    """Integration test the production client."""

    @staticmethod
    def _create_new_histograms() -> List[Histogram]:
        new_histograms = copy.deepcopy(HISTOGRAMS)
        for histo in new_histograms:
            histo["name"] = f"{histo['name']}_{uuid.uuid4().hex}"
        return new_histograms

    @staticmethod
    def _get_updated_histo(
        old_histo: Histogram, newer_histo_values: Histogram
    ) -> Histogram:
        updated_histo = copy.deepcopy(old_histo)

        bin_values = [
            b1 + b2
            for b1, b2 in zip(old_histo["bin_values"], newer_histo_values["bin_values"])
        ]
        updated_histo["bin_values"] = bin_values
        updated_histo["overflow"] += newer_histo_values["overflow"]
        updated_histo["underflow"] += newer_histo_values["underflow"]
        updated_histo["nan_count"] += newer_histo_values["nan_count"]

        return updated_histo

    @staticmethod
    def test_histo(db_rc: RestClient) -> None:  # pylint: disable=R0914
        """Run posts with updating."""

        def assert_get(histo: Histogram) -> None:
            get_body = {
                "database": "test_histograms",
                "collection": "TEST",
                "name": histo["name"],
            }
            get_resp = db_rc.request_seq("GET", "/histogram", get_body)
            assert get_resp["histogram"] == histo
            assert get_resp["history"]

        histograms = TestDBServerProdRole._create_new_histograms()
        # use first histogram for updating values in all histograms
        new_bin_values = histograms[0]["bin_values"]  # value will be incremented
        new_overflow = histograms[0]["overflow"]  # value will be incremented
        new_underflow = histograms[0]["underflow"]  # value will be incremented
        new_nan_count = histograms[0]["nan_count"]  # value will be incremented

        # Test!
        for orignial_histo in histograms:
            # 1. POST with no update flag
            post_body_1 = {
                "database": "test_histograms",
                "collection": "TEST",
                "histogram": orignial_histo,
            }
            post_resp_1 = db_rc.request_seq("POST", "/histogram", post_body_1)
            assert post_resp_1["history"]
            assert post_resp_1["histogram"] == orignial_histo
            assert not post_resp_1["updated"]

            # GET
            assert_get(orignial_histo)

            # 2. POST again with no update flag
            post_body_2 = {
                "database": "test_histograms",
                "collection": "TEST",
                "histogram": orignial_histo,
            }
            with pytest.raises(requests.exceptions.HTTPError) as e:
                _ = db_rc.request_seq("POST", "/histogram", post_body_2)
                assert e.response.status_code == 409  # Conflict Error

            # GET
            assert_get(orignial_histo)

            # 3. POST with update
            newer_histo = copy.deepcopy(orignial_histo)
            newer_histo["bin_values"] = new_bin_values
            newer_histo["overflow"] = new_overflow
            newer_histo["underflow"] = new_underflow
            newer_histo["nan_count"] = new_nan_count
            post_body_3 = {
                "database": "test_histograms",
                "collection": "TEST",
                "histogram": newer_histo,
                "update": True,
            }
            post_resp_3 = db_rc.request_seq("POST", "/histogram", post_body_3)
            assert post_resp_3["histogram"] == TestDBServerProdRole._get_updated_histo(
                orignial_histo, newer_histo
            )
            assert post_resp_3["updated"]
            assert len(post_resp_3["history"]) == 2

            # GET
            assert_get(
                TestDBServerProdRole._get_updated_histo(orignial_histo, newer_histo)
            )

        db_rc.close()

    @staticmethod
    def _create_new_files() -> List[str]:
        new_files = [f"{uuid.uuid4().hex}.txt" for i in range(6)]
        return sorted(new_files)

    @staticmethod
    def test_file(db_rc: RestClient) -> None:
        """Run some test posts."""
        collection_name = f"TEST-{uuid.uuid4().hex}"

        def assert_get(_files: List[str]) -> None:
            get_body = {"database": "test_histograms", "collection": collection_name}
            get_resp = db_rc.request_seq("GET", "/files/names", get_body)
            assert get_resp["files"] == _files
            assert get_resp["history"]

        # 1. POST with no update flag
        files = TestDBServerProdRole._create_new_files()
        post_body_1 = {
            "database": "test_histograms",
            "collection": collection_name,
            "files": files,
        }
        post_resp_1 = db_rc.request_seq("POST", "/files/names", post_body_1)
        assert post_resp_1["files"] == files
        assert post_resp_1["history"]

        # GET
        assert_get(files)

        # 2. POST again with no update flag
        post_body_2 = {
            "database": "test_histograms",
            "collection": collection_name,
            "files": files,
        }
        with pytest.raises(requests.exceptions.HTTPError) as e:
            _ = db_rc.request_seq("POST", "/files/names", post_body_2)
            assert e.response.status_code == 409  # Conflict Error

        # GET
        assert_get(files)

        # 3. POST with update but no new files
        post_body_3 = {
            "database": "test_histograms",
            "collection": collection_name,
            "files": files,
            "update": True,
        }
        post_resp_3 = db_rc.request_seq("POST", "/files/names", post_body_3)
        assert post_resp_3["files"] == files
        assert len(post_resp_3["history"]) == 2

        # GET
        assert_get(files)

        # 4. POST with update flag and new files
        new_files = TestDBServerProdRole._create_new_files()
        post_body_4 = {
            "database": "test_histograms",
            "collection": collection_name,
            "files": new_files,
            "update": True,
        }
        post_resp_4 = db_rc.request_seq("POST", "/files/names", post_body_4)
        assert post_resp_4["files"] == sorted(set(files) | set(new_files))
        assert len(post_resp_4["history"]) == 3

        # GET
        assert_get(sorted(set(files) | set(new_files)))  # set-add files

        db_rc.close()
