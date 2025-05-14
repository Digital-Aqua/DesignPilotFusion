from typing import Any

from designpilot import DpApp
from .asyncloop import FusionAsyncLoopMixin
from .logging import FusionLogMixin
from .manifest import FusionManifestMixin


__all__ = [ "FusionDpApp" ]


class FusionDpApp(
    FusionLogMixin,
    FusionAsyncLoopMixin,
    FusionManifestMixin,
    DpApp
):
    """ Patches DpApp into a Fusion environment. """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def fusion_run(self) -> None:
        self._log.info("FusionDpApp: Add-in starting.")
        self._start_async_loop()
        self._loop.run_until_complete(self.run())

    def fusion_stop(self) -> None:
        self._log.info("FusionDpApp: Add-in stopping.")
        self._loop.run_until_complete(self.stop())
