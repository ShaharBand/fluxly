from enum import Enum


class EndpointType(str, Enum):
    CLI = "cli"
    API = "api"
