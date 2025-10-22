import logging
import sys
from typing import Any
from datetime import timezone

from loguru import logger
from pydantic import BaseModel, ConfigDict

from flowcli.services.logger.config import LoggerConfig


class LoggerService(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: LoggerConfig
    handlers: list[logging.Handler] = []
    extra_params: dict[str, str] = {}

    def model_post_init(self, __context: Any) -> None:
        logger.remove()
        self.set_extra_params(extra_params={})

    def set_extra_params(self, extra_params: dict[str, str]):
        self.extra_params = extra_params
        self.configure()

    def configure(self):
        log_handler = {
            "sink": sys.stdout,
            "level": self.config.level,
            "format": self.__format_record,
            "diagnose": False,
        }
        config = {
            "handlers": [log_handler],
            "extra": self.extra_params,
        }
        if self.config.file:
            file_handler = dict(log_handler)
            file_handler["sink"] = self.config.file
            file_handler["serialize"] = True
            config["handlers"].append(file_handler)

        for handler in self.handlers:
            custom_handler = dict(log_handler)
            custom_handler["sink"] = handler
            config["handlers"].append(custom_handler)

        logger.configure(**config)

    def add_handler(self, handler) -> None:
        self.handlers.append(handler)
        self.configure()

    def remove_handler(self, handler) -> None:
        if handler in self.handlers:
            self.handlers.remove(handler)
        self.configure()

    def info(self, msg: str):
        logger.info(self.__wrap_message(msg))

    def debug(self, msg: str):
        logger.debug(self.__wrap_message(msg))

    def warning(self, msg: str):
        logger.warning(self.__wrap_message(msg))

    def error(self, msg: str):
        logger.error(self.__wrap_message(msg))

    def exception(self, msg: str):
        logger.exception(self.__wrap_message(msg))

    def __wrap_message(self, msg: str) -> str:
        if not isinstance(msg, str):
            msg = str(msg)

        return msg if len(msg) <= self.config.max_print_length else msg[: self.config.max_print_length - 3] + "..."

    def __format_record(self, record) -> str:
        dt_local = record["time"].astimezone()  # keep local timezone
        time_local_str = dt_local.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        epoch_ms = int(record["time"].timestamp() * 1000)
        level_name = record["level"].name

        extra_keys = list(self.extra_params.keys())
        extras_section = ""
        if extra_keys:
            extras_values = " ".join(
                f"{key}={record['extra'].get(key, '')}" for key in extra_keys
            )
            extras_section = f"- {extras_values} "

        prefix = f"{time_local_str} {epoch_ms} - {level_name} {extras_section}- "

        message = record["message"]
        if not isinstance(message, str):
            message = str(message)

        # escape braces for loguru
        message = message.replace("{", "{{").replace("}", "}}")

        lines = message.splitlines() or [""]
        return "\n".join(prefix + line for line in lines) + '\n'
