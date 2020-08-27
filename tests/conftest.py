import pytest
from osprey.testing import make_mock_urls


@pytest.fixture
def conftest_make_mock_urls(config, requests_mock):
    return make_mock_urls(config, requests_mock)
