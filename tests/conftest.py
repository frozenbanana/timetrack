import pytest
from pathlib import Path
from timetrack.cli import TimeTracker

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("data")

@pytest.fixture
def mock_data_file(test_data_dir):
    return test_data_dir / "test_timetrack_data.json"
