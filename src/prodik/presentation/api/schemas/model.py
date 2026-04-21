from pydantic import BaseModel


class GetModelInfoResponse(BaseModel):
    version: str
    nickname: str


class ProcessRawContentRequest(BaseModel):
    text: str
