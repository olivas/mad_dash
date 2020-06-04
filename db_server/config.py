"""Config settings."""


EXPECTED_CONFIG = {
    'MAD_DASH_AUTH_ALGORITHM': 'HS512',  # 'RS256',
    'MAD_DASH_AUTH_ISSUER': 'http://localhost:8888',  # 'maddash',
    'MAD_DASH_AUTH_SECRET': 'secret',
    'MAD_DASH_MONGODB_AUTH_USER': '',  # None means required to specify
    'MAD_DASH_MONGODB_AUTH_PASS': '',  # empty means no authentication required
    'MAD_DASH_MONGODB_HOST': 'localhost',
    'MAD_DASH_MONGODB_PORT': '27017',
    'MAD_DASH_REST_HOST': 'localhost',
    'MAD_DASH_REST_PORT': '8080',
}


AUTH_PREFIX = "maddash"


EXCLUDE_DBS = ['system.indexes', 'production', 'local',
               'simprod_filecatalog', 'config', 'token_service', 'admin']
