from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    gameName: str
    tagLine: str
    first_blood_wr: int
    ward_placed_wr: int