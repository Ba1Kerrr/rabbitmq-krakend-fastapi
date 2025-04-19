from fastapi import FastAPI, Request, requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import pika
import json

app = FastAPI()

app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"], 
                   allow_methods=["*"],
                     allow_headers=["*"], 
                   expose_headers=["*"], 
                   )

@app.post("/publish")
async def publish(request: Request):
    try:
      data = await request.json()
      connection = await pika.AsyncConnection(pika.ConnectionParameters("amqp://localhost:5672/"))
      channel = await connection.channel()
      await channel.queue_declare(queue="tasks", durable=True)
      await channel.basic_publish(
          exchange="",
          routing_key="tasks",
          body=json.dumps(data),
          properties=pika.BasicProperties(delivery_mode=2)
      )
      await connection.close()
    except RequestValidationError as e:
        return JSONResponse(content={"error": "Invalid JSON data"}, status_code=400)
    return JSONResponse(content={"status": "sent"}, status_code=200)