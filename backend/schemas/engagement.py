from pydantic import BaseModel, Field
from datetime import datetime


class CommentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    name: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedComments(BaseModel):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int


class ViewCountResponse(BaseModel):
    total_views: int
    today_views: int
    unique_visitors: int


class ViewTrackRequest(BaseModel):
    page: str = "/"
