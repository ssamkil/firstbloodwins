from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    gameName: str
    tagLine: str
    first_blood_wr: int
    ward_placed_wr: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()