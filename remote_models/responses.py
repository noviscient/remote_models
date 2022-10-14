from typing import Any, List, Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Any]


class FailedResponse(BaseModel):
    detail: str
