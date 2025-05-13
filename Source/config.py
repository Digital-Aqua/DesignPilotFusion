import json, os

with open(os.path.join(os.path.dirname(__file__), "manifest.json")) as f:
    manifest = json.load(f)

# Well-known globals for Fusion add-ins.
DEBUG = "-debug" in manifest["version"]
ADDIN_NAME = manifest["name"]
COMPANY_NAME = manifest["company"]

# Additional globals.
ADDIN_VERSION = manifest["version"]
