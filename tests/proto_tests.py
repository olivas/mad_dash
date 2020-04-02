"""Just a few tests. Nothing official here."""
import argparse
import asyncio
import subprocess
from urllib.parse import quote

import requests
from rest_tools.client import RestClient


def ingest_data(dump_path):
    """Ingest mongodb bson dump."""
    subprocess.check_call(f"mongorestore {dump_path}".split())


async def test_queries():
    """Run some test queries."""
    token_json = requests.get('http://localhost:8888/token?scope=maddash:web').json()
    md_rc = RestClient('http://localhost:8080', token=token_json['access'], timeout=5, retries=3)

    databases = await md_rc.request('GET', '/databases')
    print(databases)

    for d in [good for good in databases['databases'] if good not in ['config', 'token_service']]:
        collections = await md_rc.request('GET', f'/{quote(d)}/collections')
        print(collections)
        for c in collections['collections']:
            histograms = await md_rc.request('GET', f'/{quote(d)}/{quote(c)}/histograms')
            print(histograms)
            for h in histograms['histograms']:
                histo = await md_rc.request('GET', f'/{quote(d)}/{quote(c)}/histogram/{quote(h)}')
                print(histo)
            filelist = await md_rc.request('GET', f'/{quote(d)}/{quote(c)}/files')
            print(filelist)

    md_rc.close()


def main():
    """Main."""
    action_choices = ['ingest', 'test-queries']

    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-path', dest='dump_path', help='path to mongodump', default='./dump')
    parser.add_argument('actions', metavar='ACTIONS', nargs='*',
                        help='actions to perform.', choices=action_choices + ['all'])
    args = parser.parse_args()

    # Perform actions
    if 'all' in args.actions:
        args.actions = action_choices

    if 'ingest' in args.actions:
        ingest_data(args.dump_path)

    if 'test-queries' in args.actions:
        asyncio.get_event_loop().run_until_complete(test_queries())


if __name__ == '__main__':
    main()
