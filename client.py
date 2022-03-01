import sys
import asyncio

from .utils.logger import get_logger
from .utils.constants import (
    ERROR_EXIT_CODE,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_ENCODING
)


class AIOClient:
    def __init__(
        self,
        host: str = DEFAULT_SERVER_HOST,
        port: int = DEFAULT_SERVER_PORT,
    ) -> None:
        self.host = host
        self.port = port

        self._asyncio_loop: asyncio.events.AbstractEventLoop = (
            asyncio.get_event_loop()
        )
        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def _open_connection(
        self
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        try:
            reader, writer = await asyncio.open_connection(
                self.host,
                self.port
            )
        except OSError:
            self._logger.error(
                'Connection has not been established to the address (%s, %s)'
                ' due to an exception below:\n',
                self.host, self.port
                exc_info=True
            )
            sys.exit(ERROR_EXIT_CODE)
        else:
            self._logger.info(
                'Connection has been established to the address (%s, %s).',
                self.host, self.port
            )
            return reader, writer

    async def _close_connection(self, writer: asyncio.StreamWriter) -> None:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            self._logger.error(
                'Connection has not been closed to the address (%s, %s)'
                ' due to an exception below:\n',
                self.host, self.port
                exc_info=True
            )
            sys.exit(ERROR_EXIT_CODE)
        else:
            self._logger.info(
                'Connection to the address (%s, %s) has been closed.',
                self.host, self.port
            )

    async def _write_data(self, writer: asyncio.StreamWriter, data: str) -> None:
        try:
            writer.write(data.encode(encoding=DEFAULT_ENCODING))
            await writer.drain()
        except OSError:
            self._logger.error(
                'Error while writing data (%s) due to an exception below:\n',
                data
                exc_info=True
            )
        else:
            self._logger.info(
                'Data has been sent successfully: %s.', data
            )

    async def _read_data(self, reader: asyncio.StreamReader) -> None:
        try:
            data = await reader.read(DEFAULT_BATCH_SIZE)
        except OSError:
            self._logger.error(
                'Error while reading data from remote host'
                ' due to an exception below:\n'
                exc_info=True
            )
        else:
            self._logger.info(
                'Data has been received successfully: %s.', data
            )
            return data.decode(encoding=DEFAULT_ENCODING)

    def __repr__(self):
        return f'<AIOClient({self.host}, {self.port}) object at {id(self)}>'
