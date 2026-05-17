"""Pydantic schemas for the privacy-preserving OT API."""

from pydantic import BaseModel, Field


class CreateOTSessionRequest(BaseModel):
    # group_id is allowed because it reveals only a public group, not the exact book.
    group_id: str = Field(default="default")


class OTStepRequest(BaseModel):
    session_id: str
    level: int
    h0: int
    h1: int


class ClearOTSessionRequest(BaseModel):
    session_id: str
