from typing import ClassVar

from pydantic import BaseModel

from fluxly.services.logger.config import LoggerConfig
from fluxly.services.logger.logger import LoggerService


class Services(BaseModel):
    _logger_instance: ClassVar[LoggerService] = None

    @classmethod
    def get_logger(cls) -> LoggerService:
        if cls._logger_instance is None:
            cls._logger_instance = LoggerService(
                config=LoggerConfig(),
            )
        return cls._logger_instance
