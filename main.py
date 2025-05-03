# from fastapi import FastAPI, Request, responses
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.exceptions import RequestValidationError

# from faststream.rabbit.fastapi import RabbitRouter
# from faststream import FastStream

# from rabbitmq.rabbitmq import produser, consumer

# faststream = FastStream(broker)

# app = FastAPI()

# app.add_middleware(CORSMiddleware, 
#                    allow_origins=["*"], 
#                    allow_methods=["*"],
#                    allow_headers=["*"], 
#                    expose_headers=["*"], 
#                    )

# router = RabbitRouter("amqp://admin:admin@rabbitmq:5672/")

# @app.post("/send_message")
# async def send_message_endpoint(message: str):
#     await produser(message)
#     return responses.JSONResponse(content={"message": "Message sent"}, status_code=200)


# @faststream.route("/stream")
# async def stream():
#     while True:
#         message = await consumer()
#         if message:
#             yield message
#         else:
#             yield None


# app.include_router(router)


from fastapi import FastAPI, Request, responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from faststream.rabbit.fastapi import RabbitRouter
from faststream import FastStream

from rabbitmq.rabbitmq import produser, consumer

faststream = FastStream("amqp://admin:admin@rabbitmq:5672/")

app = FastAPI()

router = RabbitRouter("amqp://admin:admin@rabbitmq:5672/")

@app.get("/stream")
async def stream():
    async def event_generator():
        async for message in router.stream("my_queue"):
            yield {"message": message}
    return responses.StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/send_message")
async def send_message_endpoint(message: str):
    await router.send("my_queue", message)
    return {"message": "Message sent successfully"}
