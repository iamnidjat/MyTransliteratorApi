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

class AuthenticatedUser(BaseModel):
    id: int
    name: str
    email: str

class Authenticate(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: AuthenticatedUser
