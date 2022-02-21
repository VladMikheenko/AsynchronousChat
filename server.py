import asyncio
from typing import Union

from .utils.logger import get_logger
from .utils.constants import ERROR_EXIT_CODE


class AIOServer:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 54321,
    ) -> None:
        self.host = host
        self.port = port

        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug(f'{self.__repr__()} has been initialized.')

    async def start_server(self) -> None:
        await asyncio.start_server(self._serve, self.host, self.port)

    async def terminate_server(self) -> None:
        pass

    async def _serve(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        address = writer.get_extra_info('peername')

        if not address:
            self._close_connection_to_client_on_getpeername_error(writer)

        client_ip_address, _ = address
        self._logger.info(f'{client_ip_address} has connected.')

        while True:
            data = await self._read_data(reader)

            if not data:
                self._logger.info(f'{client_ip_address} has disconnected.')
                await self._close_client_connection(writer, client_ip_address)
                # As there is no more connection between client <-> server,
                # Just gracefully terminate coroutine returning None.
                return

            self._write_data(data)

    async def _write_data(
        writer: asyncio.StreamWriter,
        data: Union[bytes, bytearray]
    ) -> None:
        try:
            writer.write(data)
            await writer.drain()
        except OSError:
            self._logger.error(
                'An error occured while writing data:\n',
                exc_info=True
            )
        else:
            self._logger.info('Data has been successfully written.')

    async def _read_data(reader: asyncio.StreamReader, limit: int = -1):
        try:
            return reader.read(limit)
        except OSError:
            self._logger.error(
                'An error occured while reading data:\n',
                exc_info=True
            )
        else:
            self._logger.info(
                ('Data has been successfully read'
                 f' ({limit} bytes).' if limit else '.')
            )

    async def _close_connection_to_client_on_getpeername_error(
        self,
        writer: asyncio.StreamWriter
    ) -> None:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            self._logger.error(
                ('Connection to the client with a not defined IP'
                 ' has not been closed due to an exception below:\n'),
                exc_info=True
            )
        else:
            self._logger.info(
                ('Connection to the client with a not defined IP'
                 ' has been closed.')
            )

    async def _close_client_connection(
        self,
        writer: asyncio.StreamWriter,
        client_ip_address: str
    ) -> None:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            self._logger.error(
                (f'Connection to the client {client_ip_address}'
                 ' has not been closed due to an exception below:\n'),
                exc_info=True
            )
        else:
            self._logger.info(
                (f'Connection to the client {client_ip_address}'
                 ' has been closed.')
            )

    def __repr__(self):
        return f'<AIOServer({self.host}, {self.port}) object at {id(self)}>'
