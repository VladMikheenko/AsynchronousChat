from ..server import AIOServer
from .common import TEST_HOST, TEST_PORT


def test_aioserver_can_be_created():
    assert AIOServer(), 'AIOServer instance cannot be created.'


def test_aioserver_can_be_created_with_custom_arguments():
    assert AIOServer(host=TEST_HOST, port=TEST_PORT), \
        'AIOServer instance cannot be created with custom arguments.'


async def test_aioserver_can_be_run():
    assert (
        await AIOServer().start_server()
    ), 'AIOServer\'s instance async method `start_server` does not work.'


async def test_aioserver_can_be_stopped():
    aioserver = AIOServer()
    await aioserver.close_server(await aioserver.start_server())
    assert not server.is_serving(), \
        'AIOServer\'s instance async method `close_server` does not work.'
