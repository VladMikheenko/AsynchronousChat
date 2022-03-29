import asyncio
from typing import Optional

from .constants import DEFAULT_ENCODING, BYTES_READ_LIMIT


class AIO:
    """Serves as the backbone of AIOServer and AIOClient.

    May refer to non-existing attributes,
    so all subclasses must implement them.

    Because of the reason above must not be instantiated directly.
    """
    async def _write_data(
        self,
        writer: asyncio.StreamWriter,
        data: str
    ) -> None:
        try:
            writer.write(data.encode(encoding=DEFAULT_ENCODING))
            await writer.drain()
        except OSError:
            self._logger.error(
                'Error while writing data (%s) due to an exception below:\n',
                data.strip(),
                exc_info=True
            )
        else:
            self._logger.debug(
                'Data has been sent successfully: %s.', data.strip()
            )

    async def _read_data(
        self,
        reader: asyncio.StreamReader, limit = BYTES_READ_LIMIT
    ) -> Optional[str]:
        try:
            data = (await reader.read(limit)).decode(DEFAULT_ENCODING)
        except OSError:
            self._logger.error(
                'Error while reading data due to an exception below:\n',
                exc_info=True
            )
        else:
            self._logger.error(
                'Data has been received successfully: %s.', data.strip()
            )
            return data
