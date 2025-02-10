# from pydantic import BaseModel, Field


# class AnecdoteModel(BaseModel):
#     content: str = Field(..., min_length=5, max_length=4096)
#     user_id: int


# class RateModelUserId(BaseModel):
#     user_id: int


# class RateModel(BaseModel):
#     anecdote_id: int
#     user_id: int
#     rating: int
