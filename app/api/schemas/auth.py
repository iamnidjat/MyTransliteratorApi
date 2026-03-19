from pydantic import BaseModel, Field
from datetime import datetime


class Login(BaseModel):
    username: str = Field(
        ...,
        description="Enter your username",
        example="john_doe"
    )
    password: str = Field(
        ...,
        description="Enter your password",
        example="strongpassword123"
    )

class SignUp(BaseModel):
    username: str = Field(
        ...,
        description="Make up username",
        example="john_doe"
    )
    password: str = Field(
        ...,
        description="Make up password",
        example="strongpassword123"
    )
    email: str = Field(
        ...,
        description="Enter your email",
        example="youremail@gmail.com"
    )

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

class SuccessfulAuthentication(BaseModel):
    business_code: str
    data: Authenticate

class SuccessfulPwdChange(BaseModel):
    response_code: int = 200
    response_message: str = "success"
    user_id: int
    updated_at: datetime

class ChangePassword(BaseModel):
    email: str
    pwd: str
    new_pwd: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"