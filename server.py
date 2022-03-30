import asyncio
from typing import Optional

from .utils.classes import AIO
from .utils.functions import get_logger
from .utils.constants import (
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_ENCODING
)


class AIOServer(AIO):
    def __init__(
        self,
        host: str = DEFAULT_SERVER_HOST,
        port: int = DEFAULT_SERVER_PORT,
    ) -> None:
        self._host = host
        self._port = port

        self._connected_clients: list[asyncio.StreamWriter] = []
        self._asyncio_server: Optional[asyncio.base_events.Server] = None
        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def start_server(self) -> asyncio.events.AbstractServer:
        self._asyncio_server = (
            await asyncio.start_server(
                self._preprocess,
                self._host,
                self._port
            )
        )

        self._logger.info(
            '| Server has been started on (%s, %s).'
            '\n| Ready to accept connections...', self._host, self._port
        )
        return self._asyncio_server

    async def _preprocess(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        address = writer.get_extra_info('peername')

        if not address:
            self._close_connection_to_client_on_getpeername_error(writer)

        ip_address, *_ = address
        self._connected_clients.append(writer)
        self._logger.info('%s has connected.', ip_address)

        await self._process(reader, writer, ip_address)

    async def _process(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        ip_address: str
    ) -> None:
        while True:
            data = await self._read_data(reader)

            if not data:
                self._logger.info('%s has sent EOF.', ip_address)
                await self._close_client_connection(writer, ip_address)
                # As there is no more connection between client <-> server,
                # Just gracefully terminate coroutine returning None.
                return

            _ = asyncio.create_task(
                self._broadcast(writer, ip_address, data)
            )

    async def _broadcast(
        self,
        sender_writer: asyncio.StreamWriter,
        sender_ip_address: str,
        data: str,
    ) -> None:
        for writer in self._connected_clients:
            if writer is not sender_writer:
                await self._write_data(writer, f'{sender_ip_address}: {data}')

    async def _close_connection_to_client_on_getpeername_error(
        self,
        writer: asyncio.StreamWriter
    ) -> None:
        try:
            writer.write(
                'Sorry, server count not identify your IP.'
                .encode(DEFAULT_ENCODING)
            )

            if writer.can_write_eof():
                write.write_eof()

            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except OSError:
            self._logger.error(
                'Connection to the client with a not defined IP'
                ' has not been closed due to an exception below:\n',
                exc_info=True
            )
        else:
            self._logger.debug(
                'Connection to the client with a not defined IP'
                ' has been closed.'
            )

    async def _close_client_connection(
        self,
        writer: asyncio.StreamWriter,
        ip_address: str
    ) -> None:
        try:
            writer.close()
            await writer.wait_closed()
            self._connected_clients.remove(writer)
        except OSError:
            self._logger.error(
                'Connection to the client %s'
                ' has not been closed due to an exception below:\n',
                ip_address,
                exc_info=True
            )
        else:
            self._logger.debug(
                'Connection to the client %s has been closed.',
                ip_address
            )

    def __repr__(self):
        return f'<AIOServer({self._host}, {self._port}) object at {id(self)}>'


async def run_server():
    aioserver = AIOServer()
    asyncio_server = await aioserver.start_server()

    async with asyncio_server:
        await asyncio_server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server())
