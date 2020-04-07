"""Just a few tests. Nothing official here."""
import argparse
import asyncio
import subprocess

import requests
from rest_tools.client import RestClient


def ingest_data(dump_path):
    """Ingest mongodb bson dump."""
    subprocess.check_call(f"mongorestore {dump_path}".split())


HISTOGRAM = {'bin_values': [9, 9, 15, 8, 10, 18, 18, 25, 26, 28, 36, 35, 36, 34, 42, 33, 28, 37, 30, 41, 27, 21, 22, 33, 41, 32, 34, 36, 37, 36, 36, 38, 32, 32, 36, 40, 29, 40, 42, 35, 46, 38, 41, 37, 50, 41, 52, 67, 70, 58, 70, 86, 95, 94, 161, 174, 201, 154, 171, 190, 268, 343, 436, 453, 462, 416, 395, 301, 230, 200, 159, 113, 80,
                            74, 57, 41, 47, 46, 42, 48, 38, 39, 39, 34, 37, 37, 24, 35, 30, 20, 29, 21, 23, 31, 31, 30, 24, 34, 25, 37],
             'name': 'OnlineL2_SplineMPE_TruncatedEnergy_DOMS_MuonCosZenith',
             'underflow': 0,
             'xmax': 1,
             'xmin': -1,
             'overflow': 0,
             'expression': "cos(frame['OnlineL2_SplineMPE_TruncatedEnergy_DOMS_Muon'].dir.zenith)",
             'nan_count': 0}


async def post(update=False):
    """Run some test queries."""
    token_json = requests.get('http://localhost:8888/token?scope=maddash:production').json()
    md_rc = RestClient('http://localhost:8080', token=token_json['access'], timeout=5, retries=0)

    print('\n')

    post_body = {'database': 'simprod_histograms',
                 'collection': 'TEST',
                 'histogram': HISTOGRAM,
                 'update': update}
    print(f"POST request: {post_body}")
    post_response = await md_rc.request('POST', f"/histograms", post_body)
    print(f"POST response: {post_response}")

    print('\n')

    get_body = {'database': 'simprod_histograms',
                'collection': 'TEST',
                'name': HISTOGRAM['name']}
    print(f"GET request: {get_body}")
    get_histo = await md_rc.request('GET', f"/histograms", get_body)
    print(f"GET response: {get_histo}")

    print('\n')


async def test_queries():
    """Run some test queries."""
    token_json = requests.get('http://localhost:8888/token?scope=maddash:web').json()
    md_rc = RestClient('http://localhost:8080', token=token_json['access'], timeout=5, retries=0)

    databases = await md_rc.request('GET', '/databases')
    print(databases)

    for d in databases['databases']:
        db_request_body = {'database': d}
        collections = await md_rc.request('GET', f'/collections', db_request_body)
        print(collections)
        for c in collections['collections']:
            coll_request_body = {'database': d, 'collection': c}
            histograms = await md_rc.request('GET', f'/collections/histograms', coll_request_body)
            print(histograms)
            for h in histograms['histograms']:
                histo_request_body = {'database': d, 'collection': c, 'name': h}
                histo = await md_rc.request('GET', f'/histograms', histo_request_body)
                print(histo)
            filelist = await md_rc.request('GET', f'/files', coll_request_body)
            print(filelist)

    md_rc.close()


def main():
    """Main."""
    action_choices = ['ingest', 'test-queries', 'post', 'update']

    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-path', dest='dump_path', help='path to mongodump', default='./dump')
    parser.add_argument('actions', metavar='ACTIONS', nargs='*',
                        help='actions to perform.', choices=action_choices)
    args = parser.parse_args()

    # Perform actions
    if 'ingest' in args.actions:
        ingest_data(args.dump_path)

    if 'post' in args.actions:
        asyncio.get_event_loop().run_until_complete(post())

    if 'update' in args.actions:
        asyncio.get_event_loop().run_until_complete(post(update=True))

    if 'test-queries' in args.actions:
        asyncio.get_event_loop().run_until_complete(test_queries())


if __name__ == '__main__':
    main()
