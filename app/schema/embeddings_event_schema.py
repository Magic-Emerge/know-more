from typing import Optional

from pydantic import BaseModel, validator

from app.enums.embedding_file_types import EmbeddingFileType
from app.enums.notify_status_types import NotifyStatusType


class FileEmbedEvent(BaseModel):
    """FileEmbedEvent  schema.
    embedding 的文件信息
    """

    biz_id: int
    biz_name: str
    file_name: str
    file_type: str
    http_url: str
    renter_id: int

    @classmethod
    @validator("file_type")
    def file_type_validate(cls, v):
        allow_types = [_type.value for _type in EmbeddingFileType]
        if v not in allow_types:
            raise ValueError(f"file_type must be in {allow_types}")
        return v


class EmbedNotify(BaseModel):

    """
        完成嵌入后通知
    """
    biz_id: int
    status: str
    failed_reason: Optional[str] = None

    @classmethod
    @validator("status")
    def file_type_validate(cls, v):
        allow_types = [_type.value for _type in NotifyStatusType]
        if v not in allow_types:
            raise ValueError(f"file_type must be in {allow_types}")
        return v

    @classmethod
    def embed_notify_to_dict(cls):
        return {
            'biz_id': cls.biz_id,
            'status': cls.status,
            'failed_reason': cls.failed_reason
        }
