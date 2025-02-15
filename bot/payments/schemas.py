from pydantic import BaseModel, Field


class GiftTextModel(BaseModel):
    text: str = Field(max_length=255)


class GiftModel(BaseModel):
    from_user_id: int
    to_user_id: int
    gift_id: str
    text: str | None
    telegram_payment_charge_id: str


class DonationModel(BaseModel):
    user_id: int
    amount: int
    telegram_payment_charge_id: str


class DonationAmountModel(BaseModel):
    amount: int = Field(..., ge=1, le=100000)
