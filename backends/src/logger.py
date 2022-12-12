import logging
from pythonjsonlogger import jsonlogger
import env

# SETUP
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# HANDLERS
# --- json (for production, but enabled for local to make sure we don't get logger errs)
logFileHandler = logging.FileHandler(filename='/var/log/docker-service-log.json')
supported_keys = [
    'asctime',
    # 'created',
    'filename',
    'funcName',
    'levelname',
    # 'levelno',
    'lineno',
    # 'module',
    # 'msecs',
    'message',
    # 'name',
    # 'pathname',
    # 'process',
    # 'processName',
    # 'relativeCreated',
    # 'thread',
    # 'threadName'
]
log_format = lambda x: ['%({0:s})s'.format(i) for i in x]
custom_format = ' '.join(log_format(supported_keys))
formatter = jsonlogger.JsonFormatter(custom_format)
logFileHandler.setFormatter(formatter)
logger.addHandler(logFileHandler)

# --- stream (for local dev)
if (env.env_is_local()):
    logStreamHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(custom_format)
    logStreamHandler.setFormatter(formatter)
    logger.addHandler(logStreamHandler)
