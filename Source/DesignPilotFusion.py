import inspect, os, sys, traceback
from importlib.machinery import SourceFileLoader, ModuleSpec, SOURCE_SUFFIXES
from pathlib import Path
from typing import Any, Sequence
from types import FrameType, ModuleType

import adsk.core


_log = adsk.core.Application.get().log
_file_path = Path(__file__).resolve()
_addin_dir = _file_path.parent.resolve()
_pkg_dir = (_addin_dir / "Packages").resolve()


class DpfMetaPathFinder():
    """
    A custom module loader for our Packages directory.
    Workaround for Fusion's quirky package importer.
    """
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None
    ) -> ModuleSpec | None:
        
        # Skip relative imports
        if fullname.startswith("."):
            return None
        
        # Resolve nominal package path
        pkg_path = _pkg_dir / os.path.sep.join(fullname.split("."))

        # Ensure we're in our own add-in
        # (don't interfere with other add-ins)
        # TODO: Look into better isolation using a proxy module,
        # allowing multiple add-ins to use the same name.
        def stack(frame: FrameType | None):
            while True:
                if not frame: break
                yield Path(frame.f_code.co_filename).resolve()
                frame = frame.f_back
        if not any(
            f.is_relative_to(_addin_dir)
            for f in stack(inspect.currentframe())
        ):
            return None

        # Check for modules
        for suffix in SOURCE_SUFFIXES:
            file_path = (pkg_path).with_suffix(suffix)
            if file_path.is_file():
                _log(f"DesignPilotFusion: Found module: '{str(file_path)}'")
                result = ModuleSpec(
                    name = fullname,
                    loader = SourceFileLoader(fullname, str(file_path)),
                    origin = str(file_path)
                )
                result.has_location = True
                _log(f"DesignPilotFusion: has_location '{result.has_location}'")
                return result
        
        # Check for packages
        for suffix in SOURCE_SUFFIXES:
            init_path = pkg_path / f"__init__{suffix}"
            if init_path.is_file():
                _log(f"DesignPilotFusion: Found package: {str(init_path)}")
                result = ModuleSpec(
                    name = fullname,
                    loader = SourceFileLoader(fullname, str(init_path)),
                    origin = str(init_path),
                    is_package = True
                )
                result.has_location = True
                _log(f"DesignPilotFusion: has_location '{result.has_location}'")
                return result

        # No match found
        return None


_meta_path_finder = DpfMetaPathFinder()
_app: Any = None


def run(context: Any):
    """ Starts the Fusion add-in. """
    try:
        global _app
        sys.meta_path.insert(0, _meta_path_finder)
        from designpilot_fusion import FusionDpApp
        _app = FusionDpApp()
        _app.fusion_run("run")
        _log(f"DesignPilotFusion: Started.")
    except Exception :
        _log(f"DesignPilotFusion: Failed to start.\n{traceback.format_exc()}")
        sys.meta_path.remove(_meta_path_finder)


def stop(context: Any):
    """ Stops the Fusion add-in. """
    try:
        global _app
        if _app:
            _app.fusion_stop("stop")
        _app = None
        _log(f"DesignPilotFusion: Stopped.")
    except Exception:
        _log(f"DesignPilotFusion: Failed to stop.\n{traceback.format_exc()}")
    finally:
        if _meta_path_finder in sys.meta_path:
            sys.meta_path.remove(_meta_path_finder)
