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
    Filter to keep only that which is below and including a given log level.
    Defaults to filter out anything above level 'WARNING'.
    """
    def __init__(self, level="WARNING"):
        self.level = getattr(logging, level)

    def filter(self, record):
        return record.levelno <= self.level

class LogHandler(logging.StreamHandler):
    """
    Custom StreamHandler to use custom format when component is given
    and to replace the message terminator with a custom value.
    """
    def format(self, record):
        # If no component, then use the default formatter instead of the configured one
        if record.component:
            fmt = self.formatter
        else:
            fmt = logging.Formatter()
        return fmt.format(record)

    def emit(self, record):
        self.terminator = record.end
        super().emit(record)

# Configuration object for INFO, WARNING, and ERROR logs to stdout and stderr
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
            "format": "%(before)s%(colour)s[%(levelname)s] [%(component)s]" + RESET + " %(message)s",
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

# Logging functions
def pvpkg_log_info(component, message, before="", end="\n"):
    """
    Print INFO level log message.
    Output follows format:
        <before>[INFO] [<component>] <message>...<end>

    before: String prepended before rest of output.
    end: String appended after message. Defaults to a newline.
    """
    logger.info(message, extra={ 'component': component, 'colour': GREEN, 'before': before, 'end': end })

def pvpkg_log_warning(component, message, before="", end="\n"):
    """
    Print WARNING level log message.
    Output follows format:
        <before>[WARNING] [<component>] <message>...<end>

    before: String prepended before rest of output.
    end: String appended after message. Defaults to a newline.
    """
    logger.warning(message, extra={ 'component': component, 'colour': YELLOW, 'before': before, 'end': end })

def pvpkg_log_error(component, message, before="", end="\n"):
    """
    Print ERROR level log message.
    Output follows format:
        <before>[ERROR] [<component>] <message>...<end>

    before: String prepended before rest of output.
    end: String appended after message. Defaults to a newline.
    """
    logger.error(message, extra={ 'component': component, 'colour': RED, 'before': before, 'end': end })

def pvpkg_log(message, level=logging.INFO, before="", end="\n"):
    """
    Print <level> log message (defaults to INFO level) *without* formatting.
    Acts as a replacement for print() but outputs to whatever the logger is configured to.
    Useful for outputs with sensitive formatting like tables, where the "[<LOG LEVEL>] [<COMPONENT>]" prefix is unwanted.
    Output follows format:
        <before><message>...<end>

    level options:
        DEBUG: 10
        INFO: 20
        WARNING: 30
        ERROR: 40
    before: String prepended before rest of output.
    end: String appended after message. Defaults to a newline.
    """
    logger.log(level, message, extra = { 'component': None, 'before': before, 'end': end })
