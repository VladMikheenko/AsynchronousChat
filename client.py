import sys
import queue
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
        self._queue = queue.Queue()

        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def connect(self) -> None:
        reader, writer = await self._open_connection()

        asyncio.get_event_loop().run_in_executor(
            None,
            self._read_and_enqueue_input
        )
        _ = asyncio.create_task(self._consume_data(reader))

        while True:
            await self._write_data(writer=writer, data=self._queue.get())
            self._queue.task_done()

        await self._close_connection(writer=writer)

    def _read_and_enqueue_input(self):
        while True:
            self._queue.put(input('-> '))

    async def _consume_data(self, reader: asyncio.StreamReader) -> None:
        while True:
            data = await self._read_data(reader)

            if not data:
                return

            print(data, flush=True)

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
