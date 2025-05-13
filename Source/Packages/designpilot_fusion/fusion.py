import json, logging, os
from typing import Any, Callable

from designpilot import DpApp
import adsk.core


__all__ = [ "FusionDpApp" ]


_log_map : dict[int, adsk.core.LogLevels] = {
    logging.DEBUG: adsk.core.LogLevels.InfoLogLevel,
    logging.INFO: adsk.core.LogLevels.InfoLogLevel,
    logging.WARNING: adsk.core.LogLevels.WarningLogLevel,
    logging.ERROR: adsk.core.LogLevels.ErrorLogLevel,
    logging.CRITICAL: adsk.core.LogLevels.ErrorLogLevel,
}


_ContextCallable = Callable[[str], None]


class FusionDpApp(DpApp):
    """
    Patches DpApp into a Fusion environment.
    """

    def __init__(self, **kwargs: Any):
        with open(os.path.join(
            os.path.dirname(__file__),
            "../../DesignPilotFusion.manifest"
        ), "r") as f:
            manifest = json.load(f)
        super().__init__(
            debug = "-debug" in manifest["version"],
            **kwargs
        )

        self._manifest = manifest
        self._app = adsk.core.Application.get()
        self._ui = self._fusion_app.userInterface
        self._log.addFilter(self._fusion_log)


    def fusion_run(self, context: str) -> None:
        try:
            # create a task runner and enqueue 'self.run()'
            raise NotImplementedError("TODO")
        except Exception as e:
            e.add_note(f"Context: {context}")
            self._log.error(f"Error in fusion_run: {e}", exc_info=True)
    

    def fusion_stop(self, context: str) -> None:
        try:
            self.stop()
        except Exception as e:
            e.add_note(f"Context: {context}")
            self._log.error(f"Error in fusion_stop: {e}", exc_info=True)


    def _fusion_log(self, record: logging.LogRecord) -> logging.LogRecord:
        """ Dispatches logs to Fusion's logging systems. """

        # Console
        print(record)

        # Fusion log file
        self._app.log(
            record.msg,
            _log_map[record.levelno],
            adsk.core.LogTypes.FileLogType
        )

        # Fusion UI console
        self._app.log(
            record.msg,
            _log_map[record.levelno],
            adsk.core.LogTypes.ConsoleLogType
        )
        
        return record

