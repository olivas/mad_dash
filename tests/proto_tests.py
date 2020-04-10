"""Just a few tests. Nothing official here."""
import argparse
import asyncio
import inspect
import subprocess
import sys

import requests
from rest_tools.client import RestClient


def ingest(dump_path='./dump'):
    """Ingest mongodb bson dump."""
    subprocess.check_call(f"mongorestore {dump_path}".split())


HISTOGRAM = {'bin_values': [9, 9, 15, 8, 10, 18, 18, 25, 26, 28, 36, 35, 36, 34, 42, 33, 28, 37, 30, 41, 27, 21, 22, 33, 41, 32, 34, 36, 37, 36, 36, 38, 32, 32, 36, 40, 29, 40, 42, 35, 46, 38, 41, 37, 50, 41, 52, 67, 70, 58, 70, 86, 95, 94, 161, 174, 201, 154, 171, 190, 268, 343, 436, 453, 462, 416, 395, 301, 230, 200, 159, 113, 80,
                            74, 57, 41, 47, 46, 42, 48, 38, 39, 39, 34, 37, 37, 24, 35, 30, 20, 29, 21, 23, 31, 31, 30, 24, 34, 25, 37],
             'name': 'OnlineL2_SplineMPE_TruncatedEnergy_DOMS_MuonCosZenith',
             'underflow': 1,
             'xmax': 1,
             'xmin': -1,
             'overflow': 2,
             'expression': "cos(frame['OnlineL2_SplineMPE_TruncatedEnergy_DOMS_Muon'].dir.zenith)",
             'nan_count': 3}


def post(do_update=False):
    """Run some test posts."""
    async def _post(do_update):
        token_json = requests.get('http://localhost:8888/token?scope=maddash:production').json()
        md_rc = RestClient('http://localhost:8080',
                           token=token_json['access'], timeout=5, retries=0)

        print('\n')

        post_body = {'database': 'simprod_histograms',
                     'collection': 'TEST',
                     'histogram': HISTOGRAM,
                     'update': do_update}
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

    asyncio.get_event_loop().run_until_complete(_post(do_update))


def update():
    """Run posts with updating."""
    post(do_update=True)


FILES = ['file_one.txt', 'file_two.txt', 'file_three.txt',
         'file_four.txt', 'file_five.txt', 'file_six.txt', ]


def post_file(do_update=False):
    """Run some test posts."""
    async def _post_file(do_update):
        token_json = requests.get('http://localhost:8888/token?scope=maddash:production').json()
        md_rc = RestClient('http://localhost:8080',
                           token=token_json['access'], timeout=5, retries=0)

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

    asyncio.get_event_loop().run_until_complete(_post_file(do_update))


def update_file():
    """Run posts with updating."""
    post_file(do_update=True)


def get():
    """Run some test queries."""
    async def _get():
        token_json = requests.get('http://localhost:8888/token?scope=maddash:web').json()
        md_rc = RestClient('http://localhost:8080',
                           token=token_json['access'], timeout=5, retries=0)

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

    asyncio.get_event_loop().run_until_complete(_get())


def main():
    """Main."""
    # get all functions in this file
    action_choices = [o[1] for o in inspect.getmembers(
        sys.modules[__name__]) if (inspect.isfunction(o[1]) and o[0] != 'main')]

    parser = argparse.ArgumentParser()
    parser.add_argument('actions', metavar='ACTIONS', nargs='*',
                        help='actions to perform.', choices=[a.__name__ for a in action_choices])
    args = parser.parse_args()

    # Perform actions
    for action in args.actions:
        getattr(sys.modules[__name__], action)()


if __name__ == '__main__':
    main()
