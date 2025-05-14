import asyncio
from typing import Callable

from adsk.core import Application, CustomEventArgs, CustomEventHandler

from .dpapp import DpApp
from .fusionbase import FusionMixinBase


class FusionEventHandler(CustomEventHandler):
    """ Event handler for Fusion's CustomEvent. """

    def __init__(
        self,
        id: str,
        app: Application,
        notify_callback: Callable[[CustomEventArgs], None]
    ):
        super().__init__()
        self._id = id
        self._app = app
        self._event = app.registerCustomEvent(id)
        self._event.add(self)
        self._notify_callback = notify_callback

    def trigger(self):
        self._app.fireCustomEvent(self._id)

    def notify(self, args: CustomEventArgs) -> None:
        self._notify_callback(args)

    def detach(self):
        self._event.remove(self)


ASYNC_EVENT_ID = "designpilot_fusion_async_event"


class FusionAsyncLoopMixin(FusionMixinBase, DpApp):
    """ Mixin for managing an asyncio event loop integrated with Fusion's CustomEvent. """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._async_event_handler = FusionEventHandler(
            ASYNC_EVENT_ID,
            self._app,
            self._on_async_event
        )
        self._stop = asyncio.Future()
        self._loop = asyncio.get_event_loop()
        
    def _start_async_loop(self):
        """ Starts the asyncio loop. """
        self._request_loop()

    def _request_loop(self):
        """ Called to request an iteration of the asyncio loop. """
        self._async_event_handler.trigger()

    def _on_async_event(self, args: CustomEventArgs):
        """ Called shortly after ASYNC_EVENT_ID is triggered. """
        # Run all tasks scheduled for the current iteration.
        self._loop.call_soon(self._loop.stop)
        self._loop.run_forever()
        # Queue the next iteration.
        if self._stop.done():
            self._async_event_handler.detach()
        else:
            self._request_loop()

    async def stop(self):
        """ Stops the asyncio loop. """
        await DpApp.stop(self)
        self._stop.set_result(True)
