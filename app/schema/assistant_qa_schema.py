import re
from pydantic import BaseModel, validator
from typing import Optional, List, Union

from app.config import conf
from app.enums.embedding_file_types import EmbeddingFileType
from app.schema.chat_response_schema import ChatResponse


class EmbeddingFile(BaseModel):
    url: str
    file_name: str
    file_type: str

    @validator("file_type")
    def file_type_validate(cls, v):
        allow_types = [_type.value for _type in EmbeddingFileType]
        if v not in allow_types:
            raise ValueError(f"file_type must be in {allow_types}")
        return v


class EmbeddingRequest(BaseModel):
    files: List[EmbeddingFile]
    collection_name: Optional[str] = conf.DEFAULT_COLLECTION_NAME

    @validator("collection_name")
    def collection_name_validate(cls, v):
        pattern = r'^\w{1,30}$'

        if re.match(pattern, v) is None:
            raise ValueError("collection name can only contain numbers, letters and underscores, "
                             "and must be within 30 characters in length.")
        return v


class EmbeddingResponse(BaseModel):
    code: int
    message: str
    data: Union[bool, str]


class AssistantQaRequest(BaseModel):
    question: str
    chat_history: Optional[List]
    collection_name: Optional[str] = conf.DEFAULT_COLLECTION_NAME

    @validator("collection_name")
    def collection_name_validate(cls, v):
        pattern = r'^\w{1,30}$'

        if re.match(pattern, v) is None:
            raise ValueError("collection name can only contain numbers, letters and underscores, "
                             "and must be within 30 characters in length.")
        return v


class AssistantQaResponse(BaseModel):
    code: int
    message: str
    data: Union[ChatResponse, str]
