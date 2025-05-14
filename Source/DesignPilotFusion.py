import builtins, inspect, os, traceback
from enum import Enum, auto
from importlib.machinery import SourceFileLoader, SOURCE_SUFFIXES
from pathlib import Path
from typing import Any, Callable
from types import FrameType, ModuleType

import adsk.core


# Enable to show package loader trace logs.
TRACE = True

# Data structures
class PackageType(Enum):
    PACKAGE = auto()
    MODULE = auto()
    NOT_FOUND = auto()

# Logs
_log = adsk.core.Application.get().log
_log_trace_pkg = (
    lambda x, *args: _log(f"Package loader: {x.format(*args)}")
    if TRACE else
    lambda x: None
)

# Paths
_filename = Path(__file__).resolve().name
_here = inspect.currentframe().f_code.co_filename
_prefix = _here[:-len(_filename)] # Format must match `co_filename`
_pkg_dir = ( Path(__file__).parent / "Packages" ).resolve()

# __import__ utils
_ImportMethod = Callable[
    [ str, dict | None, dict | None, list[str] | None, int | None ],
    ModuleType
]
_import_base: _ImportMethod | None = None

# Caches
_packages: dict[str, tuple[Path, PackageType]] = {}
_ignore: set[str] = set()
_loaded_modules: dict[str, ModuleType] = {}

# The main app instance.
_app: Any = None


def _check_package(name: str) -> tuple[Path, PackageType]:
    """
    Checks if a package exists in our add-in.

    Returns:
        tuple[Path, PackageType]: The path to the package and its type.
    """

    if name in _ignore:
        return (None, PackageType.NOT_FOUND)
    
    if name in _packages:
        return _packages[name]
    
    path = _pkg_dir / os.path.sep.join(name.split("."))
    
    # Check for modules
    for suffix in SOURCE_SUFFIXES:
        file_path = path.with_suffix(suffix)
        if file_path.is_file():
            _log_trace_pkg("Found module file: {}", file_path)
            _packages[name] = (file_path, PackageType.MODULE)
            return _packages[name]
        
    # Check for packages
    for suffix in SOURCE_SUFFIXES:
        init_path = path / f"__init__{suffix}"
        if init_path.is_file():
            _log_trace_pkg("Found package directory: {}", init_path)
            _packages[name] = (init_path, PackageType.PACKAGE)
            return _packages[name]
    
    # Not found
    _log_trace_pkg("Not found: {}", name)
    _ignore.add(name)
    return (None, PackageType.NOT_FOUND)


def _import_package(
        name: str,
        globals: dict | None = None,
        locals: dict | None = None,
        fromlist: list[str] | None = None,
        level: int | None = None,
    ) -> ModuleType | None:
    """
    Imports a package from our add-in.

    Returns:
        ModuleType | None: The imported module, or None if the package
        is not found.
    """
    if name in _loaded_modules:
        _log_trace_pkg("Found module in cache: {}", name)
        return _loaded_modules[name]

    path, package_type = _check_package(name)
    if package_type == PackageType.NOT_FOUND:
        return None

    if package_type == PackageType.MODULE:
        loader = SourceFileLoader(name, str(path))
        module = loader.load_module(name)
        _loaded_modules[name] = module
        return module
    
    if package_type == PackageType.PACKAGE:
        loader = SourceFileLoader(name, str(path))
        module = loader.load_module(name)
        module.__path__ = [str(path.parent)]
        module.__package__ = name
        _loaded_modules[name] = module
        return module


def _frame_stack(frame: FrameType | None, skip: int = 1):
    """
    Returns a generator of frames from the call stack.

    Args:
        frame: The starting frame.
        skip: The number of frames to skip.
    """
    if frame:
        for _ in range(skip):
            frame = frame.f_back
    while frame:
        yield frame
        frame = frame.f_back


def _import_wrapper(
        name: str,
        globals: dict | None = None,
        locals: dict | None = None,
        fromlist: list[str] | None = None,
        level: int | None = None,
    ) -> ModuleType:
    """
    Monkey-patches `__import__` to locate our packages.

    While this kind of hack is generally not recommended (for good reasons),
    this actually appears to be the safest way to provide package isolation
    between Fusion add-ins.

    Defers to existing `__import__` if the package is not in our collection.

    Returns:
        ModuleType: The imported module.
    """
    _log_trace_pkg("Checking import of {}", name)

    try:
        # Quick exit: 
        if (
            # Skip relative imports
            name.startswith(".")
            # Skip ignored imports
            or name in _ignore
        ):
            _log_trace_pkg("Skipping import of {}", name)
            return _import_base(name, globals, locals, fromlist, level)

        # Are we in our own add-in?
        for frame in _frame_stack(inspect.currentframe()):
            if frame.f_code.co_filename.startswith(_prefix):
                _log_trace_pkg("Importing package {} from our add-in.", name)
                result = _import_package(name, globals, locals, fromlist, level)
                if result: return result
        _log_trace_pkg("Not in our add-in, skipping import of {}", name)
    except:
        _log(f"Unexpected error checking module {name}. Skipping import.\n{traceback.format_exc()}")
    
    # Fallback to standard import
    return _import_base(name, globals, locals, fromlist, level)


def run(context: Any):
    """ Fusion entrypoint. """
    try:
        # Patch __import__ to support our package collection.
        _log_trace_pkg("Patching __import__")
        global _import_base
        _import_base = builtins.__import__
        if builtins.__import__ != _import_wrapper:
            builtins.__import__ = _import_wrapper
        else:
            _log("Error: __import__ is already patched.")

        # Start the add-in.
        from designpilot_fusion import FusionDpApp
        global _app
        _app = FusionDpApp()
        _log(f"Starting DesignPilotFusion.")
        _app.fusion_run()
        _log(f"Started DesignPilotFusion.")
    
    except Exception :
        _log(f"DesignPilotFusion: Failed to start.\n{traceback.format_exc()}")


def stop(context: Any):
    """ Fusion stop signal. """
    try:
        # Stop the add-in.
        global _app
        if _app and hasattr(_app, 'fusion_stop'):
            _log(f"DesignPilotFusion: Stopping.")
            _app.fusion_stop()
        _app = None
        _log(f"DesignPilotFusion: Stopped.")

    except:
        _log(f"DesignPilotFusion: Failed to stop.\n{traceback.format_exc()}")

    try:
        # Unpatch __import__ to restore the original import behavior.
        _log("Unpatching __import__")
        global _import_base
        if builtins.__import__ != _import_wrapper:
            _log("Error: Can't unpatch: __import__ is not patched, or has been patched over.")
        builtins.__import__ = _import_base

    except:
        _log(f"DesignPilotFusion: Failed to unpatch.\n{traceback.format_exc()}")
