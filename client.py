import queue
import asyncio
from typing import Optional

from .utils.classes import AIO
from .utils.functions import get_logger
from .utils.constants import (
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_ENCODING,
    DELAY_OF_QUEUE_GET_NOWAIT
)


class AIOClient(AIO):
    def __init__(
        self,
        host: str = DEFAULT_SERVER_HOST,
        port: int = DEFAULT_SERVER_PORT,
    ) -> None:
        self._host = host
        self._port = port

        self._queue = queue.Queue()
        self._event_loop = asyncio.get_event_loop()
        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def start_client(self) -> None:
        reader, writer = await self._open_connection()

        self._event_loop.run_in_executor(
            None,
            self._read_and_enqueue_data
        )
        await asyncio.gather(
            self._send_data(writer),
            self._receive_data(reader),
            return_exceptions=True
        )
        await self._close_connection(writer=writer)

    def _read_and_enqueue_data(self) -> None:
        while True:
            data = input()

            if not data:
                continue

            self._queue.put(data)

    async def _send_data(self, writer: asyncio.StreamWriter) -> None:
        while True:
            try:
                await self._write_data(
                    writer=writer,
                    data=self._queue.get_nowait()
                )
            except queue.Empty: 
                await asyncio.sleep(DELAY_OF_QUEUE_GET_NOWAIT)
            else:
                self._queue.task_done()

    async def _receive_data(self, reader: asyncio.StreamReader) -> None:
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
                self._host,
                self._port
            )
        except OSError:
            self._logger.error(
                'Connection has not been established to the address (%s, %s)'
                ' due to an exception below:\n',
                self._host, self._port,
                exc_info=True
            )
        else:
            self._logger.debug(
                'Connection has been established to the address (%s, %s).',
                self._host, self._port
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
                self._host, self._port,
                exc_info=True
            )
        else:
            self._logger.debug(
                'Connection to the address (%s, %s) has been closed.',
                self._host, self._port
            )

    def __repr__(self):
        return f'<AIOClient({self._host}, {self._port}) object at {id(self)}>'


if __name__ == '__main__':
    aioclient = AIOClient()
    asyncio.run(aioclient.start_client())
