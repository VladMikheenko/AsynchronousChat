from ..server import AIOServer
from .common import TEST_HOST, TEST_PORT


def test_aioserver_can_be_created():
    assert AIOServer(), 'AIOServer instance cannot be created.'


def test_aioserver_can_be_created_with_custom_arguments():
    assert AIOServer(host=TEST_HOST, port=TEST_PORT), \
        'AIOServer instance cannot be created with custom arguments.'
