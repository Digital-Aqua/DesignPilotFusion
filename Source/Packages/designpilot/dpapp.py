import logging
from typing import Any


__all__ = [ "DpApp" ]


class DpApp(object):

    def __init__(self, *,
        debug: bool = False,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._debug = debug
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(logging.DEBUG if self._debug else logging.INFO)


    async def run(self) -> None:
        raise NotImplementedError("TODO")


    def stop(self) -> None:
        raise NotImplementedError("TODO")

