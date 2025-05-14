import json
from pathlib import Path

from .fusionbase import FusionMixinBase


class FusionManifestMixin(FusionMixinBase):
    """ Mixin supporting the add-in manifest. """

    def __init__(self):
        super().__init__()
        manifest_path = Path(__file__).parent / "../../DesignPilotFusion.manifest"
        with open(manifest_path, "r") as f:
            self._manifest = json.load(f)
        self.debug = "-debug" in self._manifest["version"]
