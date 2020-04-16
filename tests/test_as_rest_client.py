"""Just a few tests. Nothing official here."""
import pytest
import requests
from rest_tools.client import RestClient


def _setup_rest_client():
    token_json = requests.get('http://localhost:8888/token?scope=maddash:web').json()
    md_rc = RestClient('http://localhost:8080',
                       token=token_json['access'], timeout=5, retries=0)
    return md_rc


HISTOGRAMS = [{'bin_values': [9, 9, 15, 8, 10, 18, 18, 25, 26, 28, 36, 35, 36, 34, 42, 33, 28, 37,
                              30, 41, 27, 21, 22, 33, 41, 32, 34, 36, 37, 36, 36, 38, 32, 32, 36,
                              40, 29, 40, 42, 35, 46, 38, 41, 37, 50, 41, 52, 67, 70, 58, 70, 86,
                              95, 94, 161, 174, 201, 154, 171, 190, 268, 343, 436, 453, 462, 416,
                              395, 301, 230, 200, 159, 113, 80, 74, 57, 41, 47, 46, 42, 48, 38, 39,
                              39, 34, 37, 37, 24, 35, 30, 20, 29, 21, 23, 31, 31, 30, 24, 34, 25, 37],
               'name': 'OnlineL2_SplineMPE_TruncatedEnergy_DOMS_MuonCosZenith',
               'underflow': 1,
               'xmax': 1,
               'xmin': -1,
               'overflow': 2,
               'expression': "cos(frame['OnlineL2_SplineMPE_TruncatedEnergy_DOMS_Muon'].dir.zenith)",
               'nan_count': 3}
              ]


@pytest.mark.asyncio
async def test_post(do_update=False):
    """Run some test posts."""
    md_rc = _setup_rest_client()

    for histo in HISTOGRAMS:
        print('\n')

        post_body = {'database': 'test_histograms',
                     'collection': 'TEST',
                     'histogram': histo,
                     'update': do_update}
        print(f"POST request: {post_body}")
        post_response = await md_rc.request('POST', f"/histogram", post_body)
        print(f"POST response: {post_response}")

        print('\n')

        get_body = {'database': 'test_histograms',
                    'collection': 'TEST',
                    'name': histo['name']}
        print(f"GET request: {get_body}")
        get_histo = await md_rc.request('GET', f"/histogram", get_body)
        print(f"GET response: {get_histo}")

        print('\n')


@pytest.mark.asyncio
async def test_update():
    """Run posts with updating."""
    await test_post(do_update=True)


FILES = ['file_one.txt', 'file_two.txt', 'file_three.txt',
         'file_four.txt', 'file_five.txt', 'file_six.txt', ]


@pytest.mark.asyncio
async def test_post_file(do_update=False):
    """Run some test posts."""
    md_rc = _setup_rest_client()

    print('\n')

    post_body = {'database': 'simprod_histograms',
                 'collection': 'TEST',
                 'files': FILES,
                 'update': do_update}
    print(f"POST request: {post_body}")
    post_response = await md_rc.request('POST', f"/files", post_body)
    print(f"POST response: {post_response}")

    print('\n')

    get_body = {'database': 'simprod_histograms',
                'collection': 'TEST'}
    print(f"GET request: {get_body}")
    get_histo = await md_rc.request('GET', f"/files", get_body)
    print(f"GET response: {get_histo}")

    print('\n')


@pytest.mark.asyncio
async def test_update_file():
    """Run posts with updating."""
    await test_post_file(do_update=True)


@pytest.mark.asyncio
async def test_get():
    """Run some test queries."""
    md_rc = _setup_rest_client()

    databases = await md_rc.request('GET', '/databases/names')
    print(databases)

    for d in databases['databases']:
        db_request_body = {'database': d}
        collections = await md_rc.request('GET', f'/collections/names', db_request_body)
        print(collections)
        for c in collections['collections']:
            coll_request_body = {'database': d, 'collection': c}
            histograms = await md_rc.request('GET', f'/collections/histograms/names', coll_request_body)
            print(histograms)
            for h in histograms['histograms']:
                histo_request_body = {'database': d, 'collection': c, 'name': h}
                histo = await md_rc.request('GET', f'/histogram', histo_request_body)
                print(histo)
            filelist = await md_rc.request('GET', f'/files/names', coll_request_body)
            print(filelist)

    md_rc.close()
