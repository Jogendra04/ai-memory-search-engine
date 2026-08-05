from pydantic import BaseModel, EmailStr
from typing import List


class ChatRequest(BaseModel):
    question: str


class MemoryRequest(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class RegisterRequest(BaseModel):

    name: str

    email: EmailStr

    password: str


class LoginRequest(BaseModel):

    email: EmailStr

    password: str