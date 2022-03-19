import sys
import asyncio
from typing import Optional

from .utils.classes import AIO
from .utils.logger import get_logger
from .utils.constants import (
    ERROR_EXIT_CODE, DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, DEFAULT_ENCODING
)


class AIOServer(AIO):
    def __init__(
        self,
        host: str = DEFAULT_SERVER_HOST,
        port: int = DEFAULT_SERVER_PORT,
    ) -> None:
        self.host = host
        self.port = port

        self._connected_clients: list[asyncio.StreamWriter] = []
        self._asyncio_server: Optional[asyncio.base_events.Server] = None
        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def start_server(self) -> None:
        try:
            self._asyncio_server = (
                await asyncio.start_server(
                    self._preprocess_client,
                    self.host,
                    self.port
                )
            )
        except OSError:
            self._logger.error(
                'An error occured while starting server:\n',
                exc_info=True
            )
            sys.exit(ERROR_EXIT_CODE)
        else:
            self._logger.info('Server has been started.')

    async def close_server(self) -> None:
        try:
            if not self._asyncio_server:
                logger.warning(
                    'An attempt to close non-existing server has been made.'
                )
                return
            if self._asyncio_server.is_closing():
                logger.warning(
                    'Asyncio server is closing (closed).'
                    ' No need to do it again.'
                )
                return

            self._asyncio_server.close()
            await self._asyncio_server.wait_closed()
            self._asyncio_server = None
        except OSError:
            self._logger.error(
                'An error occured while closing server:\n',
                exc_info=True
            )
        else:
            self._logger.info('Server has been closed.')

    async def _preprocess_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        address = writer.get_extra_info('peername')

        if not address:
            self._close_connection_to_client_on_getpeername_error(writer)

        client_ip_address, *_ = address
        self._connected_clients.append(writer)
        self._logger.info('%s has connected.', client_ip_address)

        await asyncio.create_task(
            self._process(reader, writer, client_ip_address)
        )

    async def _process(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        client_ip_address: str
    ) -> None:
        while True:
            data = await self._read_data(reader)

            if not data:
                self._logger.info('%s has sent EOF.', client_ip_address)
                await self._close_client_connection(writer, client_ip_address)
                # As there is no more connection between client <-> server,
                # Just gracefully terminate coroutine returning None.
                return

            _ = asyncio.create_task(
                self._broadcast(writer, client_ip_address, data)
            )

    async def _broadcast(
        self,
        sender_writer: asyncio.StreamWriter,
        sender_ip_address: str,
        data: str,
    ) -> None:
        for writer in self._connected_clients:
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
            self._logger.info(
                'Connection to the client with a not defined IP'
                ' has been closed.'
            )

    async def _close_client_connection(
        self,
        writer: asyncio.StreamWriter,
        client_ip_address: str
    ) -> None:
        try:
            writer.close()
            await writer.wait_closed()
            self._connected_clients.remove(writer)
        except OSError:
            self._logger.error(
                'Connection to the client %s'
                ' has not been closed due to an exception below:\n',
                client_ip_address,
                exc_info=True
            )
        else:
            self._logger.info(
                'Connection to the client %s has been closed.',
                client_ip_address
            )

    def __repr__(self):
        return f'<AIOServer({self.host}, {self.port}) object at {id(self)}>'


if __name__ == '__main__':
    aioserver = AIOServer()
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(aioserver.start_server())
    event_loop.run_forever()
