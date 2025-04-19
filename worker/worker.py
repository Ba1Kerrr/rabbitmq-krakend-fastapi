import pika
import json

async def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"Received task: {data}")
        await ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        await ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
async def main():
    connection = await pika.AsyncConnection(pika.ConnectionParameters("amqp://localhost:5672/"))
    channel = await connection.channel()
    await channel.queue_declare(queue="tasks", durable=True)
    await channel.basic_qos(prefetch_count=1)
    await channel.basic_consume(queue="tasks", on_message_callback=callback)
    print("Waiting for messages...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Some error,stopping consumer...")
        channel.stop_consuming()
        connection.close()
