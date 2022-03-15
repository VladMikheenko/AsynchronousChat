import sys
import asyncio
import functools
from typing import Optional

from .utils.classes import AIO
from .utils.logger import get_logger
from .utils.constants import (
    ERROR_EXIT_CODE,
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_ENCODING
)


class AIOClient(AIO):
    def __init__(
        self,
        host: str = DEFAULT_SERVER_HOST,
        port: int = DEFAULT_SERVER_PORT,
    ) -> None:
        self.host = host
        self.port = port

        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def connect(self) -> None:
        reader, writer = await self._open_connection()

        _ = asyncio.create_task(self._consume_data(reader))

        while True:
            data = input('-> ')

            if not data:
                break

            await self._write_data(writer=writer, data=data)

        await self._close_connection(writer=writer)

    async def _consume_data(self, reader: asyncio.StreamReader) -> None:
        while True:
            data = await self._read_data(reader)

            if not data:
                return

            print(data, flush=True)
            sys.stdout.flush()

    async def _open_connection(
        self
    ) -> Optional[tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        try:
            reader, writer = await asyncio.open_connection(
                self.host,
                self.port
            )
        except OSError:
            self._logger.error(
                'Connection has not been established to the address (%s, %s)'
                ' due to an exception below:\n',
                self.host, self.port,
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
                self.host, self.port,
                exc_info=True
            )
            sys.exit(ERROR_EXIT_CODE)
        else:
            self._logger.info(
                'Connection to the address (%s, %s) has been closed.',
                self.host, self.port
            )

    def __repr__(self):
        return f'<AIOClient({self.host}, {self.port}) object at {id(self)}>'


if __name__ == '__main__':
    aioclient = AIOClient()
    asyncio.run(aioclient.connect())
