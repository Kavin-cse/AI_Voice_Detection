from pydantic import BaseModel, Field
from typing import Literal

Language = Literal['Tamil', 'English', 'Hindi', 'Malayalam', 'Telugu']

class VoiceRequest(BaseModel):
    language: Language
    audioFormat: Literal['mp3']
    audioBase64: str = Field(..., min_length=100)

class SuccessResponse(BaseModel):
    status: Literal['success']
    language: Language
    classification: Literal['AI_GENERATED', 'HUMAN']
    confidenceScore: float
    explanation: str

class ErrorResponse(BaseModel):
    status: Literal['error']
    message: str
