import logging

from adsk.core import LogLevels, LogTypes
from .quirks import app_log

from .fusionbase import FusionMixinBase


_log_map : dict[int, int] = {
    logging.DEBUG:    LogLevels.InfoLogLevel,
    logging.INFO:     LogLevels.InfoLogLevel,
    logging.WARNING:  LogLevels.WarningLogLevel,
    logging.ERROR:    LogLevels.ErrorLogLevel,
    logging.CRITICAL: LogLevels.ErrorLogLevel,
}
_default_level = _log_map[logging.INFO]


class FusionLogMixin(FusionMixinBase):
    """ Mixin for Fusion-specific logging. """

    def __init__(self):
        super().__init__()
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.addFilter(self._fusion_log_handler)

    def _fusion_log_handler(self, record: logging.LogRecord) -> logging.LogRecord:
        """ Dispatches logs to Fusion's logging systems. """
        try:
            # Fusion log file
            app_log(
                self._app,
                record.getMessage(), # Use getMessage() for formatted string
                _log_map.get(record.levelno, _default_level),
                LogTypes.FileLogType
            )

            # Fusion UI console
            app_log(
                self._app,
                record.getMessage(),
                _log_map.get(record.levelno, _default_level),
                LogTypes.ConsoleLogType
            )
        except:
            pass
        return record
