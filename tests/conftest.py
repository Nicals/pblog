import pathlib
import tempfile

import pytest


@pytest.fixture(scope='function')
def temp_dir(tmpdir):
    """Builds a temporary directory. Completly removes it at the end of the
    test.

    This fixture passes the path of the temporary directory in the form of
    a pathlib.Path instance.

    The temporary directory is destroyed at the end of the test.
    """
    with tempfile.TemporaryDirectory(prefix='pblog-test-') as directory:
        dirpath = pathlib.Path(directory)
        yield dirpath
