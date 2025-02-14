from pydantic import BaseModel, Field, field_validator, AnyUrl, ValidationError
import re


class AnecdoteUserIdFilter(BaseModel):
    user_id: int


class AnecdoteFilter(BaseModel):
    id: int


class AnecdoteUpdate(BaseModel):
    report_count: int


class AnecdoteModel(BaseModel):
    content: str = Field(..., min_length=5, max_length=3900)
    user_id: int
    
    @field_validator('content')
    def validate_content(cls, v: str) -> str:
        url_pattern = re.compile(
            r'(?:https?://)?'
            r'(?:www\.)?'
            r'(?:[a-zA-Zа-яА-Я0-9](?:[a-zA-Zа-яА-Я0-9-]*[a-zA-Zа-яА-Я0-9])?\.)+'
            r'[a-zA-Zа-яА-Я]{2,}'
            r'(?:/[^\s]*)?'
        )
        
        if url_pattern.search(v.lower()):
            raise ValueError("Ссылки в анекдотах запрещены")
        return v

class RateModelUserId(BaseModel):
    user_id: int


class RateModel(BaseModel):
    anecdote_id: int
    user_id: int
    rating: int | None
