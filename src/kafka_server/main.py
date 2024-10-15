import asyncio
from aiokafka import AIOKafkaProducer

async def get_kafka_producer() -> AIOKafkaProducer:
    loop = asyncio.get_event_loop()  # Получаем текущий event loop
    producer = AIOKafkaProducer(
        loop=loop,  # Явно передаем event loop
        bootstrap_servers="localhost:9092"  # Укажи свой адрес Kafka сервера
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
