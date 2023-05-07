import os
import time
from app.config.logger import get_logger

from memphis import Memphis, MemphisError, MemphisConnectError, MemphisHeaderError
import json

from app.schema.embeddings_event_schema import FileEmbedEvent, EmbedNotify
from app.serv.qa_embeddings import qa_embeddings_files
from app.config.conf import DEFAULT_TEXT_FIELD, EMBED_FINISH_NOTIFY_STATION, EMBED_FINISH_NOTIFY_PRODUCER_NAME
from app.client.mq_client import send_message
from app.enums.notify_status_types import NotifyStatusType

logger = get_logger()


def notify_msg(biz_id: int, status: str):
    embed_notify = EmbedNotify(biz_id=biz_id, status=status)
    message_str = json.dumps(embed_notify, default=embed_notify.embed_notify_to_dict())
    await send_message(message_str, EMBED_FINISH_NOTIFY_STATION, EMBED_FINISH_NOTIFY_PRODUCER_NAME)


async def msg_handler(msgs, error, context):
    try:
        for msg in msgs:
            logger.info("handler msg info [%s]", msg)
            json_dict = json.loads(msg)
            file_embed_event = FileEmbedEvent(**json_dict)

            # 开始embedding
            notify_msg(biz_id=file_embed_event.biz_id, status=NotifyStatusType.RUNNING.value)

            embed_result, reason = qa_embeddings_files(file_name=file_embed_event.file_name,
                                                       file_type=file_embed_event.file_type,
                                                       url=file_embed_event.http_url,
                                                       collection_name=file_embed_event.biz_name,
                                                       text_field=DEFAULT_TEXT_FIELD
                                                       )

            if embed_result:
                notify_msg(biz_id=file_embed_event.biz_id, status=NotifyStatusType.FINISHED.value)
                await msg.ack()
            else:
                notify_msg(biz_id=file_embed_event.biz_id, status=NotifyStatusType.FAILED.value)

            # 获取headers
            # headers = msg.get_headers()
            if error:
                logger.error(error)
    except (MemphisError, MemphisConnectError, MemphisHeaderError) as e:
        logger.error(e)
        return


async def file_embeddings_mq():
    try:
        memphis = Memphis()
        await memphis.connect(host=os.getenv("MQ_HOST"), username="know_more", password="1qaz@WSX")

        consumer_name = f"file_embeddings_consumer_{int(time.time() * 1000) // 1000}"

        consumer = await memphis.consumer(station_name="file_embeddings", consumer_name=consumer_name,
                                          consumer_group="file_embeddings_consumer_group")
        # consumer.set_context({"key": "value"})
        consumer.consume(msg_handler)
    except (MemphisError, MemphisConnectError) as e:
        logger.error(e)

    finally:
        memphis.close()
