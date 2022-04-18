import queue
import signal
import asyncio
import threading
import contextvars
from typing import Optional

from .utils.classes import AIO
from .utils.functions import get_logger
from .utils.constants import (
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DELAY_OF_QUEUE_GET_NOWAIT,
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
        self._logger = get_logger(
            name=self.__class__.__name__.lower(),
            suffix=str(id(self))
        )
        self._logger.debug('%s has been initialized.', self.__repr__())

    async def start_client(self) -> None:
        connection_options = await self._open_connection()

        if not connection_options:
            return

        reader, writer = connection_options

        asyncio.get_event_loop().run_in_executor(
            None,
            self._read_and_enqueue_data
        )

        asyncio.gather(
            self._send_data(writer),
            self._receive_data(reader),
            return_exceptions=True
        )

        await _is_termination_required.get().wait()
        await self._close_connection(writer)

    def _read_and_enqueue_data(self) -> None:
        while not _is_termination_required.get().is_set():
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
        except OSError as e:
            self._logger.error(
                'Connection has not been established to the address (%s, %s)'
                f' due to an error below:\n{str(e)}',
                self._host, self._port,
            )
        else:
            self._logger.debug(
                'Connection has been established to the address (%s, %s).',
                self._host, self._port
            )
            return reader, writer

    async def _close_connection(self, writer: asyncio.StreamWriter) -> None:
        writer.close()
        await writer.wait_closed()

        self._logger.debug(
            'Connection to the address (%s, %s) has been closed.',
            self._host, self._port
        )

    def __repr__(self) -> str:
        return f'<AIOClient({self._host}, {self._port}) object at {id(self)}>'


async def run() -> None:
    _is_termination_required: contextvars.ContextVar[asyncio.Event] = (
        contextvars.ContextVar(
            '_is_termination_required'
        )
    )
    _is_termination_required.set(asyncio.Event())

    signal.signal(signal.SIGINT, _handle_sigint_signal)
    aioclient = AIOClient()

    task = asyncio.create_task(
        aioclient.start_client(),
        name='start-client-task'
    )

    await task


def _handle_sigint_signal(signal, frame) -> None:
    _is_termination_required.get().set()


if __name__ == '__main__':
    asyncio.run(run())
