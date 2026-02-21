from pydantic import BaseModel


class Login(BaseModel):
    username: str
    password: str

class SignUp(BaseModel):
    username: str
    password: str
    email: str

class Logout(BaseModel):
    pass