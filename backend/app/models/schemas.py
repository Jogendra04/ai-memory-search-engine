from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class MemoryRequest(BaseModel):
    title: str
    content: str