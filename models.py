from pydantic import BaseModel

class Item(BaseModel):
    id: int
    email: str
    password: str

class SignUp(BaseModel):
    email: str
    password: str
    confirm_password: str

class Signin(BaseModel):
    email: str
    password: str

class Tracker(BaseModel):
    name: str
    priceIdn: float

class TrackerDelete(BaseModel):
    name: str
