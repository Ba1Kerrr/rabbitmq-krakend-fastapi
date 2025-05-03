import aiormq

async def produser(message: str) -> None:
    connection = await aiormq.connect("")
    channel = await connection.channel()
    await channel.basic_publish(message, routing_key="my_queue")
    await connection.close()

async def consumer() -> str:
    connection = await aiormq.connect("amqp://admin:admin@rabbitmq:5672/")
    channel = await connection.channel()
    message = await channel.basic_get("my_queue")
    if message:
        await channel.basic_ack(message.delivery_tag)
        return message.body.decode("utf-8")
    else:
        return None

# import pika
# import uuid
# import json

# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()
# RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

# class RabbitMq(object):

#     def __init__(self):
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host=RABBITMQ_URL))

#         self.channel = self.connection.channel()

#         result = self.channel.queue_declare(queue='', exclusive=True)
#         self.callback_queue = result.method.queue

#         self.channel.basic_consume(
#             queue=self.callback_queue,
#             on_message_callback=self.on_response,
#             auto_ack=True)

#     def on_response(self, ch, method, props, body):
#         if self.corr_id == props.correlation_id:
#             self.response = body

#     def call(self, message):
#         self.response = None
#         self.corr_id = str(uuid.uuid4())
#         self.channel.basic_publish(
#             exchange='',
#             routing_key='ocr_service',
#             properties=pika.BasicProperties(
#                 reply_to=self.callback_queue,
#                 correlation_id=self.corr_id,
#             ),
#             body=json.dumps(message))
#         while self.response is None:
#             self.connection.process_data_events()
#         response_json = json.loads(self.response)
#         return response_json