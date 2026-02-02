from typing import Annotated

from pydantic import BaseModel, Field


class Volume(BaseModel):
    value: Annotated[float, Field(ge=0, le=1)]

    @property
    def percentage(self) -> float:
        return self.value * 100

    @classmethod
    def from_percentage(cls, percentage: float):
        return cls(value=percentage / 100)
