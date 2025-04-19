cd krakend

sudo docker build -t krakend . 
cd ../rabbitmq

sudo docker-compose up -d

uvicorn bridge.main:app --reload
