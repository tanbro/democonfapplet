HTTP_ADDRESS = '0.0.0.0'
HTTP_PORT = 8080

STATIC_PATH = '../webapp'

YTX_URL_PREFIX = 'https://sandboxapp.cloopen.com:8883/2013-12-26'

YTX_ACCOUNT_SID = 'aaf98f895350b68801535915c40e0e5c'
YTX_AUTH_TOKEN = 'cdc50c8894f14b79ad8c5aea5dc01b2f'

YTX_APP_ID = 'aaf98f895350b6880153591763dd0e64'
YTX_APP_TOKEN = 'edd2ac1cfa1acfefa6bedfc69d824c46'

YTX_SUB_ACCOUNT_SID = 'aaf98f895350b6880153591764050e65'
YTX_SUB_AUTH_TOKEN = 'a0bea007c8614d78a34d501875690186'

PRE_IMPORT_MODULES = [
    'confapplet.client_api',
]

LOGGING_CONFIG = {
    'version': 1,
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'console',
        ],
    },
    'loggers': {
        'asyncio': {
            'level': 'DEBUG',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
            'stream': 'ext://sys.stdout',
        }
    },
    'formatters': {
        'normal': {
            'format': '%(asctime)-15s [%(threadName)-10s] [%(levelname)-7s] %(name)s - %(message)s',
        },
    },
}
