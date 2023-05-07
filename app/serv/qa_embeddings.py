from app.client import oss_client
from app.config.conf import TEMP_DIR
from app.config.logger import get_logger
from app.enums.embedding_file_types import EmbeddingFileType
from app.milvus import ingest_milvus

logger = get_logger()


def qa_embeddings_files(file_name: str, file_type: str, collection_name: str, text_field: str,
                              url: str = ""):
    try:
        # 判断文件类型
        allow_types = [_type.value for _type in EmbeddingFileType]
        assert file_type in allow_types, RuntimeError(f"The file_type[{file_type}] is not allowed!")

        full_file_path = TEMP_DIR.join(file_name.join(".").join(file_type))
        res = oss_client.download_object(full_file_path)

        with open(full_file_path, "w") as text_file:
            text_file.write(res)

        if EmbeddingFileType.PDF.value == file_type:
            ingest_milvus.ingest_pdf_2_milvus(
                file_path=full_file_path,
                collection_name=collection_name,
                text_field=text_field
            )
        elif EmbeddingFileType.TXT.value == file_type:
            ingest_milvus.ingest_txt_2_milvus(
                file_path=full_file_path,
                collection_name=collection_name,
                text_field=text_field
            )
        elif EmbeddingFileType.DOCX.value == file_type:
            ingest_milvus.ingest_docx_2_milvus(
                file_path=full_file_path,
                collection_name=collection_name,
                text_field=text_field
            )
        elif EmbeddingFileType.HTML.value == file_type:
            ingest_milvus.ingest_html_2_milvus(
                file_path=full_file_path,
                collection_name=collection_name,
                text_field=text_field
            )
        elif EmbeddingFileType.HTTP.value == file_type:
            url_list = [url]
            ingest_milvus.ingest_url_2_milvus(
                collection_name=collection_name,
                text_field=text_field,
                urls=url_list
            )
        elif EmbeddingFileType.HTTPs.value == file_type:
            url_list = [url]
            ingest_milvus.ingest_url_2_milvus(
                collection_name=collection_name,
                text_field=text_field,
                urls=url_list
            )

        logger.info("embedding success：file_name[%s] or http url: [%s]", file_name, url)
    except Exception as e:
        logger.error("embedding failed：%s", str(e))
        raise RuntimeError(f"embedding failed：{str(e)}")
    return True
