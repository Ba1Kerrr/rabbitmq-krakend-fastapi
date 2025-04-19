
# KrakenD + RabbitMQ Integration Example

This example demonstrates how to set up **KrakenD** to receive an HTTP request on an endpoint and publish it to a **RabbitMQ** queue. A simple **worker service** consumes messages from the queue and processes them.

---

## Architecture Overview

```
Client --> KrakenD --> RabbitMQ --> Worker Service
```

---

## Project Structure

```
krakend-rabbitmq-example/
├── krakend/
│   ├── krakend.json
│   └── Dockerfile
├── rabbitmq/
│   └── docker-compose.yml
├── bridge/
│   └── main.py         # REST to RabbitMQ bridge
├── worker/
│   └── worker.py       # RabbitMQ consumer
```

---

## Step 1: RabbitMQ Setup

**rabbitmq/docker-compose.yml**

```yaml
version: '3.8'
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
```

Run:

```bash
docker-compose -f rabbitmq/docker-compose.yml up -d
```

---

## Step 2: REST Bridge (Python Flask)

**bridge/main.py**

```python
from flask import Flask, request, jsonify
import pika
import json

app = Flask(__name__)

@app.route("/publish", methods=["POST"])
def publish():
    data = request.json
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="tasks", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="tasks",
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return jsonify({"status": "sent"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
```

Run it:

```bash
pip install flask pika
python bridge/main.py
```

---

## Step 3: KrakenD Configuration

**krakend/krakend.json**

```json
{
  "version": 3,
  "name": "krakend-rabbitmq-gateway",
  "port": 8080,
  "timeout": "3000ms",
  "endpoints": [
    {
      "endpoint": "/send",
      "method": "POST",
      "backend": [
        {
          "host": ["http://host.docker.internal:9000"],
          "url_pattern": "/publish",
          "encoding": "json"
        }
      ]
    }
  ]
}
```

**krakend/Dockerfile**

```Dockerfile
FROM devopsfaith/krakend
COPY krakend.json /etc/krakend/krakend.json
```

Build & Run:

```bash
docker build -t krakend-rmq ./krakend
docker run --rm -it -p 8080:8080 krakend-rmq run -c /etc/krakend/krakend.json
```

---

## Step 4: Worker Consumer

**worker/worker.py**

```python
import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"Received task: {data}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="tasks", durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="tasks", on_message_callback=callback)
print("Waiting for messages...")
channel.start_consuming()
```

Run:

```bash
python worker/worker.py
```

---

## Step 5: Test the Flow

Send a request to KrakenD:

```bash
curl -X POST http://localhost:8080/send   -H "Content-Type: application/json"   -d '{"task": "generate_report", "params": {"user_id": 42}}'
```

Check terminal of `worker.py` — it should print the received task.

---

## Notes

- You can secure the bridge with auth, validation, rate-limiting.
- Replace `localhost` with actual service names if running everything in Docker.
- Use Docker Compose for full integration for prod setups.
