
from logging.config import dictConfig
from environs import Env

from importlib.metadata import Distribution

pkg = Distribution.from_name(__package__)


class Config:
    """
    Base configuration
    """
    DEBUG = False
    TESTING = False
    SERVER_VERSION = pkg.version

    def __init__(self):
        # Environment variables
        env = Env()
        env.read_env()  # also read .env file, if it exists

        self.JOB_LOGS_TAIL = env.int('JOB_LOGS_TAIL', 1000)

        self.CONTAINER_ENV = env('CONTAINER_ENV', 'swarm')
        self.STORAGE_TYPE = env('STORAGE_TYPE', 'host')

        self.REMOVE_JOBS = env('REMOVE_JOBS', 'yes').lower() != 'no'

        if self.STORAGE_TYPE == 'host' or self.STORAGE_TYPE == 'nfs':
            self.STOREBASE = env('STOREBASE')
            if self.STORAGE_TYPE == 'nfs':
                self.NFS_SERVER = env('NFS_SERVER')

        if self.CONTAINER_ENV == 'swarm':
            docker_host = env('DOCKER_HOST', '')
            if docker_host:
                self.DOCKER_HOST = docker_host
            docker_tls_verify = env.int('DOCKER_TLS_VERIFY', None)
            if docker_tls_verify is not None:
                self.DOCKER_TLS_VERIFY = docker_tls_verify
            docker_cert_path = env('DOCKER_CERT_PATH', '')
            if docker_cert_path:
                self.DOCKER_CERT_PATH = docker_cert_path

        if self.CONTAINER_ENV == 'kubernetes':
            self.JOB_NAMESPACE = env('JOB_NAMESPACE', 'default')
            self.SECURITYCONTEXT_RUN_AS_USER = env.int('SECURITYCONTEXT_RUN_AS_USER', None)
            self.SECURITYCONTEXT_RUN_AS_GROUP = env.int('SECURITYCONTEXT_RUN_AS_GROUP', None)

        if self.CONTAINER_ENV == 'cromwell':
            self.CROMWELL_URL = env('CROMWELL_URL')
            self.TIMELIMIT_MINUTES = env.int('TIMELIMIT_MINUTES')

        self.env = env


class DevConfig(Config):
    """
    Development configuration
    """
    ENV = 'development'
    DEBUG = True
    TESTING = True

    def __init__(self):
        super().__init__()

        # DEV LOGGING CONFIGURATION
        dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {
                    'format': '[%(asctime)s] [%(levelname)s]'
                              '[%(module)s:%(lineno)d %(process)d %(thread)d] %(message)s'
                },
            },
            'handlers': {
                'console_simple': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                },
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': '/tmp/debug.log',
                    'formatter': 'simple'
                }
            },
            'loggers': {
                '': {  # root logger
                    'level': 'INFO',
                    'handlers': ['console_simple'],
                },
                'pman': {  # pman package logger
                    'level': 'DEBUG',
                    'handlers': ['console_simple', 'file'],
                    'propagate': False
                    # required to avoid double logging with root logger
                },
            }
        })


class ProdConfig(Config):
    """
    Production configuration
    """
    ENV = 'production'

    def __init__(self):
        super().__init__()

        # PROD LOGGING CONFIGURATION
        dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {
                    'format': '[%(asctime)s] [%(levelname)s]'
                              '[%(module)s:%(lineno)d %(process)d %(thread)d] %(message)s'
                },
            },
            'handlers': {
                'console_simple': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                },
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': '/tmp/debug.log',
                    'formatter': 'simple'
                }
            },
            'loggers': {
                '': {  # root logger
                    'level': 'INFO',
                    'handlers': ['console_simple'],
                },
                'pman': {  # pman package logger
                    'level': 'INFO',
                    'handlers': ['file'],
                    'propagate': False
                },
            }
        })

        # Environment variables-based secrets
        # SECURITY WARNING: keep the secret key used in production secret!
        env = self.env
        self.SECRET_KEY = env('SECRET_KEY')
