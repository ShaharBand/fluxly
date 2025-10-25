from typing import Annotated

from pydantic import BaseModel, Field


class LoggerConfig(BaseModel):
    level: Annotated[str, Field("INFO", description="log level: DEBUG | INFO | WARNING | ERROR | FATAL")]
    file: Annotated[str, Field(None, description="log output file")]
    max_print_length: int = Field(10*1000, description="Maximum length of log messages before truncation")
