import logging
import logging.config

# Logging level colours
RED = str('\033[1;31m')
YELLOW = str('\033[1;33m')
GREEN = str('\033[0;32m')
RESET = str('\033[0;39m')

# Log levels
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40

class LevelFilter(logging.Filter):
    """
    Filter to keep only that below and including a given log level.
    Defaults to filter out anything above level 'WARNING'.
    """
    def __init__(self, level="WARNING"):
        self.level = getattr(logging, level)

    def filter(self, record):
        return record.levelno <= self.level

class LogFormatter(logging.Formatter):
    """
    Formatter to only apply custom format when a component is provided.
    """
    def format(self, record):
        s = record.msg
        if record.component:
            s = super().format(record)
        if not record.end:
            s.replace("a", "b")
        return s

class LogHandler(logging.StreamHandler):
    """
    Subclassed StreamHandler to replace the message terminator with a custom value.
    """
    def emit(self, record):
        self.terminator = record.end
        super().emit(record)

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
            "()": LogFormatter,
            "format": "%(colour)s[%(levelname)s] [%(component)s]" + RESET + " %(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "()": LogHandler,
            "level": "INFO",
            "formatter": "simple",
            "filters": ["excludeErr"],
            "stream": "ext://sys.stdout"
        },
        "stderr": {
            "()": LogHandler,
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
        [INFO] [<COMPONENT>] <MESSAGE>...
    """
    logger.info(message, extra={ 'component': component, 'colour': GREEN, 'end': '\n' })

# FORMAT: [<LOG LEVEL>] [<COMPONENT>] <MESSAGE>...
def pvpkg_log_warning(component, message):
    """
    Print WARNING level log message to stdout.
    Messages follow format:
        [WARNING] [<COMPONENT>] <MESSAGE>...
    """
    logger.warning(message, extra={ 'component': component, 'colour': YELLOW, 'end': '\n' })

def pvpkg_log_error(component, message):
    """
    Print ERROR level log message to stdout.
    Messages follow format:
        [ERROR] [<COMPONENT>] <MESSAGE>...
    """
    logger.error(message, extra={ 'component': component, 'colour': RED, 'end': '\n' })

def pvpkg_log(message, level=logging.INFO, end="\n"):
    """
    Print <level> (default INFO) log message to stdout *without* formatting.
    Acts as a replacement for print() but outputs to whatever the logger is configured to.
    Useful for outputs with sensitive formatting like tables, where the "[<LOG LEVEL>] [<COMPONENT>]" prefix is unwanted.
    Messages follow format:
        <Message>...<end (default newline)>

    level options:
        DEBUG: 10
        INFO: 20
        WARNING: 30
        ERROR: 40

    end: String appended after message. Defaults to a newline.
    """
    logger.log(level, message, extra = { 'component': None, 'end': end })
