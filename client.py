import queue
import signal
import asyncio
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
        reader, writer = await self._open_connection()

        asyncio.get_event_loop().run_in_executor(
            None,
            self._read_and_enqueue_data
        )
        await asyncio.gather(
            self._send_data(writer),
            self._receive_data(reader),
            return_exceptions=True
        )

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
                ' due to an error below:\n',
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
        writer.close()
        await writer.wait_closed()

        self._logger.debug(
            'Connection to the address (%s, %s) has been closed.',
            self._host, self._port
        )

    def __repr__(self) -> str:
        return f'<AIOClient({self._host}, {self._port}) object at {id(self)}>'


async def run() -> None:
    aioclient = AIOClient()

    task = asyncio.create_task(
        aioclient.start_client(),
        name='start-client-task'
    )

    await is_termination_required.wait()
    await _terminate_client()


async def _terminate_client() -> None:
    tasks_to_cancel = [
        task for task in asyncio.all_tasks()
        if task is not asyncio.current_task()
    ]

    for task in tasks_to_cancel:
        task.cancel()

    await asyncio.gather(*tasks_to_cancel, return_exception=True)


def _handle_sigint_signal(signal, frame) -> None:
    is_termination_required.set()


if __name__ == '__main__':
    is_termination_required = asyncio.Event()
    signal.signal(signal.SIGINT, _handle_sigint_signal)
    asyncio.run(run())
