"""Pytest configuration and fixtures for DadosCvm tests."""
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    """Create and return a temporary directory that will be cleaned up after the test."""
    with tempfile.TemporaryDirectory() as tempdir:
        yield Path(tempdir)
