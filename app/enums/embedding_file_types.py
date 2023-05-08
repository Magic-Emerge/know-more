

from enum import Enum, unique


@unique
class EmbeddingFileType(Enum):
    """
    向量化支持的文件类型
    """
    PDF = "pdf"
    TXT = "txt"
    CSV = "csv"
    DOC = "doc"
    DOCX = "docx"
    HTML = "html"
    HTTP = "http"
    HTTPs = "https"
    MD = "md"

