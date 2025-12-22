from pydantic import BaseModel, Optional
import datetime
from decimal import Decimal
from typing import Literal, List
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

class WalletCreate(BaseModel):
    name: str

class WalletResponse(BaseModel):
    id: str
    user_id: str
    name: str
    created_at: datetime.datetime

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: str
    user_id: str
    name: str
    created_at: datetime.datetime

class WalletBalance(BaseModel):
    wallet_id: str
    balance: Decimal

class CategoryBalance(BaseModel):
    category_id: Optional[str] = None
    balance: Decimal

class WalletCategoryBalance(BaseModel):
    wallet_id: str
    balance: List[CategoryBalance]