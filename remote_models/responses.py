from typing import Any, List, Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):
    pass


class BasePaginatedResponse(BaseResponse):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Any]


class FailedResponse(BaseResponse):
    detail: str
