"""Integration test the web client."""

# pylint: disable=redefined-outer-name

import pytest  # type: ignore
import requests

# local imports
from rest_tools.client import RestClient  # type: ignore


@pytest.fixture  # type: ignore
def db_rc() -> RestClient:
    """Get database REST client."""
    token_json = requests.get("http://localhost:8888/token?scope=maddash:web").json()
    rc = RestClient(
        "http://localhost:8080", token=token_json["access"], timeout=5, retries=0
    )
    return rc


class TestDBServerWebRole:
    """Integration test the web client."""

    @staticmethod
    def test_get(db_rc: RestClient) -> None:
        """Run some test queries."""
        databases = db_rc.request_seq("GET", "/databases/names")
        print(databases)

        for d in databases["databases"]:
            db_request_body = {"database": d}
            collections = db_rc.request_seq(
                "GET", "/collections/names", db_request_body
            )
            print(collections)
            for c in collections["collections"]:
                coll_request_body = {"database": d, "collection": c}
                histograms = db_rc.request_seq(
                    "GET", "/collections/histograms/names", coll_request_body
                )
                print(histograms)
                for h in histograms["histograms"]:
                    histo_request_body = {"database": d, "collection": c, "name": h}
                    histo = db_rc.request_seq("GET", "/histogram", histo_request_body)
                    print(histo)
                filelist = db_rc.request_seq("GET", "/files/names", coll_request_body)
                print(filelist)

        db_rc.close()

    @staticmethod
    def test_post_histo(db_rc: RestClient) -> None:
        """Failure-test role authorization."""
        post_body = {
            "database": "test_histograms",
            "collection": "TEST",
            "histogram": {"Anything": True},
        }
        with pytest.raises(requests.exceptions.HTTPError) as e:
            db_rc.request_seq("POST", "/histogram", post_body)
            assert e.response.status_code == 403  # Forbidden Error

        db_rc.close()

    @staticmethod
    def test_post_files(db_rc: RestClient) -> None:
        """Failure-test role authorization."""
        post_body = {
            "database": "test_histograms",
            "collection": "collection_name",
            "files": ["test.txt"],
        }
        with pytest.raises(requests.exceptions.HTTPError) as e:
            db_rc.request_seq("POST", "/files/names", post_body)
            assert e.response.status_code == 403  # Forbidden Error

        db_rc.close()
