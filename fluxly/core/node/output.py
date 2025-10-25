
from pydantic import BaseModel


class NodeOutput(BaseModel):
    def __str__(self) -> str:
        return self.model_dump_json(indent=2)

    def __repr__(self) -> str:
        return self.__str__()
