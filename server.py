import asyncio

from .utils.logger import get_logger


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
        pass

    def __repr__(self):
        return f'<AIOServer({self.host}, {self.port}) object at {id(self)}>'
