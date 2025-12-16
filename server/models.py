from pydantic import BaseModel, Optional
import datetime
from decimal import Decimal
from typing import Literal
class TransactionCreate(BaseModel):
    wallet_id: str
    category_id: Optional[str] = None
    amount: Decimal
    type: Literal["income", "expense"]
    description: str
    transaction_date: datetime.datetime

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    wallet_id: str
    category_id: Optional[str] = None
    amount: Decimal
    type: Literal["income", "expense"]
    description: str
    transaction_date: datetime.datetime
    created_at: datetime.datetime
