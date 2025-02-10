from pydantic import BaseModel


class UserIDModel(BaseModel):
    id: int


class TelegramIDModel(BaseModel):
    telegram_id: int


class UserModel(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
