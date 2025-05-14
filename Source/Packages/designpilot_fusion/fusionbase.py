from adsk.core import Application, UserInterface


class FusionMixinBase(object):
    """ Base class for all Fusion mixins. """

    def __init__(self):
        self._app = Application.get()

    @property
    def _app(self) -> Application:
        return Application.get()

    @property
    def _ui(self) -> UserInterface:
        return self._app.userInterface
