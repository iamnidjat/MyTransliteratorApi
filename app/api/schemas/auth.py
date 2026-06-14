from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime


class Login(BaseModel):
    username: str = Field(
        ...,
        description="Enter your username",
    )
    password: str = Field(
        ...,
        description="Enter your password",
    )

class SignUp(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Make up username",
        # example="John123!" deprecated, v1 style
        examples=["John123!"]
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Make up password",
        examples=["Strongpassword123!"]
    )
    email: EmailStr = Field(
        ...,
        description="Enter your email",
        examples=["youremail@gmail.com"]
    )

    @field_validator("username")
    def check_username(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Username must contain at least 1 uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Username must contain at least 1 number")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Username must contain at least 1 symbol")
        return v
    
    @field_validator("password")
    def check_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least 1 number")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Password must contain at least 1 symbol")
        return v

class Logout(BaseModel):
    pass

class AuthenticatedUser(BaseModel):
    id: int
    name: str
    email: EmailStr

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
    email: EmailStr
    pwd: str
    new_pwd: str = Field(
        ...,
        min_length=6,
        description="Make up new password",
        examples=["Newstrongpassword123!"]
    )

class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"