from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from fluxly.node import NodeOutput


class UserRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: Annotated[int, Field(alias="userId")]
    email: str


class ExtractOutput(NodeOutput):
    records: Annotated[
        list[UserRecord],
        Field(description="Validated user records pulled from the source"),
    ] = []
