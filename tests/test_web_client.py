"""Integration test the web client."""

# pylint: disable=redefined-outer-name

import pytest  # type: ignore
import requests
from rest_tools.client import RestClient  # type: ignore


@pytest.fixture
def db_rc():
    """Get database REST client."""
    token_json = requests.get('http://localhost:8888/token?scope=maddash:web').json()
    rc = RestClient('http://localhost:8080', token=token_json['access'], timeout=5, retries=0)
    return rc


class TestWebClient:
    """Integration test the web client."""

    @pytest.mark.asyncio
    async def test_get(self, db_rc):
        """Run some test queries."""
        databases = await db_rc.request('GET', '/databases/names')
        print(databases)

        for d in databases['databases']:
            db_request_body = {'database': d}
            collections = await db_rc.request('GET', '/collections/names', db_request_body)
            print(collections)
            for c in collections['collections']:
                coll_request_body = {'database': d, 'collection': c}
                histograms = await db_rc.request('GET', '/collections/histograms/names', coll_request_body)
                print(histograms)
                for h in histograms['histograms']:
                    histo_request_body = {'database': d, 'collection': c, 'name': h}
                    histo = await db_rc.request('GET', '/histogram', histo_request_body)
                    print(histo)
                filelist = await db_rc.request('GET', '/files/names', coll_request_body)
                print(filelist)

        db_rc.close()

    @pytest.mark.asyncio
    async def test_post_histo(self, db_rc):
        """Failure-test role authorization."""
        post_body = {'database': 'test_histograms',
                     'collection': 'TEST',
                     'histogram': {'Anything': True}}
        with pytest.raises(requests.exceptions.HTTPError) as e:
            await db_rc.request('POST', '/histogram', post_body)
            assert e.response.status_code == 403  # Forbidden Error

        db_rc.close()

    @pytest.mark.asyncio
    async def test_post_files(self, db_rc):
        """Failure-test role authorization."""
        post_body = {'database': 'simprod_histograms',
                     'collection': 'collection_name',
                     'files': ['test.txt']}
        with pytest.raises(requests.exceptions.HTTPError) as e:
            await db_rc.request('POST', '/files/names', post_body)
            assert e.response.status_code == 403  # Forbidden Error

        db_rc.close()
