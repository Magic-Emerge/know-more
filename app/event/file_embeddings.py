
import os
from memphis import Memphis, Headers, MemphisError, MemphisConnectError, MemphisHeaderError, MemphisSchemaError


async def msg_handler(msgs, error, context):
    try:
        for msg in msgs:
            print("message: ", msg.get_data())
            await msg.ack()
            headers = msg.get_headers()
            if error:
                print(error)
    except (MemphisError, MemphisConnectError, MemphisHeaderError) as e:
        print(e)
        return


async def file_embeddings_mq():
    try:
        memphis = Memphis()
        await memphis.connect(host=os.getenv("MQ_HOST"), username="know_more", password="1qaz@WSX")

        consumer = await memphis.consumer(station_name="file_embeddings", consumer_name="file_embeddings_consumer",
                                          consumer_group="file_embeddings_consumer_group")
        # consumer.set_context({"key": "value"})
        consumer.consume(msg_handler)
    except (MemphisError, MemphisConnectError) as e:
        print(e)

    finally:
        memphis.close()

