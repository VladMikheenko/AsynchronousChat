import sys
import logging
from typing import Optional


def get_logger(
    *,
    name: str,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None
) -> logging.Logger:
    _ = '-'.join(filter(None, (prefix, name, suffix)))
    logger = logging.getLogger(_)
    logger.setLevel(logging.DEBUG)

    return _adjust_logger(logger=logger, unique_identifier=_)


def _adjust_logger(
    *,
    logger: logging.Logger,
    unique_identifier: str
) -> logging.Logger:
    file_handler = logging.FileHandler(unique_identifier + '.log')
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)

    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(filename)s - %(levelname)s - %(message)s'
        )
    )

    for handler in (file_handler, stream_handler):
        logger.addHandler(handler)

    return logger


def _gracefully_terminate_serverside():
    pass


def _gracefully_terminate_clientside():
    pass
