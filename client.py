import sys
import asyncio

from .utils.logger import get_logger
from .utils.constants import ERROR_EXIT_CODE


class AIOClient:
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

    async def _open_connection(self) -> None:
        try:
            reader, writer = await asyncio.open_connection(
                self.host,
                self.port
            )
        except OSError:
            self._logger.error(
                ('Connection has not been established to the'
                 f' address ({self.host}, {self.port})'
                 f' due to an exception below:\n'),
                exc_info=True
            )
            sys.exit(ERROR_EXIT_CODE)
        else:
            self._logger.info(
                ('Connection has been established to the'
                 f' address ({self.host}, {self.port}).')
            )
            return reader, writer

    async def _close_connection(self, writer: asyncio.StreamWriter) -> None:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            self._logger.error(
                ('Connection has not been closed to the'
                 f' address ({self.host}, {self.port})'
                 f' due to an exception below:\n'),
                exc_info=True
            )
            sys.exit(ERROR_EXIT_CODE)
        else:
            self._logger.info(
                (f'Connection to the address ({self.host}, {self.port})'
                 ' has been closed.')
            )

    def __repr__(self):
        return f'<AIOClient({self.host}, {self.port}) object at {id(self)}>'
