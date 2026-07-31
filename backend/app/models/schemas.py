from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    question: str


class MemoryRequest(BaseModel):
    title: str
    content: str
    tags: List[str] = []