from __future__ import annotations
import os
from memphis import Memphis, Headers, MemphisError, MemphisConnectError, MemphisHeaderError, MemphisSchemaError


async def sendMessage(message: str):
    try:
        memphis = Memphis()
        await memphis.connect(host=os.getenv("MQ_HOST"), username="know_more", password="1qaz@WSX")

        producer = await memphis.producer(station_name="embedding_notify",
                                          producer_name="embedding_notify_producer")  # you can send the message parameter as dict as well
        headers = Headers()

        await producer.produce(message, headers=headers)

    except (MemphisError, MemphisConnectError, MemphisHeaderError, MemphisSchemaError) as e:
        print(e)

    finally:
        await memphis.close()



