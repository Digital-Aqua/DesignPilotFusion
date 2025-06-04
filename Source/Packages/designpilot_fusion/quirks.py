from adsk.core import Application


def app_log(app: Application, message: str, level: int, type: int) -> None:
    """ Type correction for adsk.core.Application.log typing quirk. """
    app.log(message, level, type) # type: ignore
