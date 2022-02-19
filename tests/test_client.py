from ..client import AIOClient
from .common import TEST_HOST, TEST_PORT


def test_aioclient_can_be_created():
    assert AIOClient(), 'AIOClient instance cannot be created.'


def test_aioclient_can_be_created_with_custom_arguments():
    assert AIOClient(host=TEST_HOST, port=TEST_PORT), \
        'AIOClient instance cannot be created with custom arguments.'
