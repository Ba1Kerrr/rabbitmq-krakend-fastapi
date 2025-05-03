cd krakend

sudo docker build -t krakend . 
cd ../rabbitmq

sudo docker-compose up -d

uvicorn bridge.main:app --reload

# ТЗ

Есть набор сервисов (микросервисов) которым нужно общаться

Вот идея была в том что они должны отправлять сообщение на эндпоинт (на faststream), тот бы ставил в очередь его (в rabbitmq)

# structure
Надо подключиться с помощью 