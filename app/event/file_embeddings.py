import os
import time
from app.config.logger import get_logger

from memphis import Memphis, Headers, MemphisError, MemphisConnectError, MemphisHeaderError, MemphisSchemaError

logger = get_logger()


async def msg_handler(msgs, error, context):
    try:
        for msg in msgs:
            print("message: ", msg.get_data())
            await msg.ack()
            headers = msg.get_headers()
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
