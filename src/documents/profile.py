from pydantic import BaseModel
from typing import Optional

class Name(BaseModel):
    first: str
    last: Optional[str] = None

class AuthProfile(BaseModel):
    email: str
    name: Name 