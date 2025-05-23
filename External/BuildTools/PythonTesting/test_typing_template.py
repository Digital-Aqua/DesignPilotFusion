# https://gist.github.com/amwaters/f1ca809c1a3ccdb058f9fb05bc679ddc

import pyright
from pathlib import Path
import MY_PACKAGE as target_package

def test_pyright_type_check():
    """
    Tests that pyright reports no errors for the package.
    """
    init_file = str(target_package.__file__) # type: ignore
    source_dir = Path(init_file).parent
    result = pyright.run( str(source_dir.absolute()) )
    
    # Assert that pyright ran successfully (return code 0)
    assert result.returncode == 0, \
        f"Pyright found type errors in {source_dir}."
