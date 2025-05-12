import asyncio
import json
import os
from fastapi import Depends, FastAPI,Request
from faststream.rabbit.fastapi import RabbitRouter, Logger

from pika import ConnectionParameters, BlockingConnection,BasicProperties,PlainCredentials

from pydantic import BaseModel

# Получаем URL RabbitMQ из переменной окружения
rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/")
router = RabbitRouter(rabbitmq_url)

connection = BlockingConnection(ConnectionParameters(rabbitmq_url))
channel = connection.channel()

# Определяем модель для входящих сообщений
class Incoming(BaseModel):
    m: dict

# def call():
#     return True

# Обработчик для входящих сообщений из очереди "test"
@router.subscriber("test")
@router.publisher("response")
async def hello(m: Incoming, logger: Logger):
    logger.info(m)
    return {"response": "Hello, Rabbit!"}

# HTTP-эндпоинт
@router.get("/")
async def hello_http():
    return "Hello, HTTP!"

# Создаем экземпляр FastAPI и подключаем маршрутизатор
app = FastAPI()

@app.post("/send_message")
async def send_message(message: str):
    data = Request.json
    try:
        channel.basic_publish(
            exchange="",
            routing_key="tasks",
            body=json.dumps(data),
            properties=BasicProperties(delivery_mode=2)
        )
        return {"message": "Message sent successfully"}
    except Exception as e:
        return {"error": "Failed to send message", "details": str(e)}

app.include_router(router)

@router.after_startup
async def startup_event(app: FastAPI):
    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"Received task: {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = BlockingConnection(ConnectionParameters(rabbitmq_url))

    channel = connection.channel()
    channel.queue_declare(queue="tasks", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="tasks", on_message_callback=callback)
    print("Waiting for messages...")
    channel.start_consuming()


