import logging
import logging.config

# Logging level colours
RED = str('\033[1;31m')
YELLOW = str('\033[1;33m')
GREEN = str('\033[0;32m')
RESET = str('\033[0;39m')

class LevelFilter(logging.Filter):
    """
    Filter to keep only that below and including a given log level.
    Defaults to filter out anything above level 'WARNING'.
    """
    def __init__(self, level="WARNING"):
        self.level = getattr(logging, level)

    def filter(self, record):
        return record.levelno <= self.level

# Configuration for three logging levels and formatting
logger_config = {
    "version": 1,
    "filters": {
        "excludeErr": {
            "()": LevelFilter,
            "level": "WARNING"
        }
    },
    "formatters": {
        "simple": {
            "format": "%(colour)s[%(levelname)s] [%(component)s]" + RESET + " %(message)s"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "filters": ["excludeErr"],
            "stream": "ext://sys.stdout"
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        }
    },
    "loggers": {
        "pvpkg_logger": {
            "level": "INFO",
            "handlers": ["stdout", "stderr"]
        }
    }
}

# Configure and get logger
logging.config.dictConfig(logger_config);
logger = logging.getLogger("pvpkg_logger");
# Set minimum log level to INFO
logger.setLevel(logging.INFO)

# Functions to output
def pvpkg_log_info(component, message):
    """
    Print INFO level log message to stdout.
    Messages follow format:
        [<LOG LEVEL>] [<COMPONENT>] <MESSAGE>...
    """
    logger.info(message, extra={ 'component': component, 'colour': GREEN })

# FORMAT: [<LOG LEVEL>] [<COMPONENT>] <MESSAGE>...
def pvpkg_log_warning(component, message):
    """
    Print WARNING level log message to stdout.
    Messages follow format:
        [<LOG LEVEL>] [<COMPONENT>] <MESSAGE>...
    """
    logger.warning(message, extra={ 'component': component, 'colour': YELLOW })

def pvpkg_log_error(component, message):
    """
    Print ERROR level log message to stdout.
    Messages follow format:
        [<LOG LEVEL>] [<COMPONENT>] <MESSAGE>...
    """
    logger.error(message, extra={ 'component': component, 'colour': RED })