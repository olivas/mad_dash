"""Just a few tests. Nothing official here."""
import asyncio

import requests
from rest_tools.client import RestClient


async def main():
    """Main."""
    token_json = requests.get('http://localhost:8888/token?scope=maddash:web').json()
    md_rc = RestClient('http://localhost:8080', token=token_json['access'], timeout=5, retries=3)

    databases = await md_rc.request('GET', '/database/names')
    print(databases)

    for d in databases['databases']:
        collections = await md_rc.request('GET', f'/{d}/collections')
        print(collections)
        for c in collections:
            histograms = await md_rc.request('GET', f'/{d}/{c}/histograms')
            print(histograms)

    md_rc.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
