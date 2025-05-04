from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel
from pydantic import BaseModel, Field


T = TypeVar('T')


#login

class Login(BaseModel):
    username: str
    password: str


#register
class Register(BaseModel):
    id: str
    username: str
    email: str
    password: str
    
    first_name: str
    last_name: str
#response
class ResponseSchema(BaseModel):
    code: int
    status: str
    message: str
    result: Optional[T] = None

#token
class TokenResponse(BaseModel):
    code: str
    status: str
    message: str
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None











