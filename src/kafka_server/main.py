import asyncio
from aiokafka import AIOKafkaProducer

async def get_kafka_producer() -> AIOKafkaProducer:
    loop = asyncio.get_event_loop()  
    producer = AIOKafkaProducer(
        loop=loop,  #
        bootstrap_servers="localhost:9092"  # Paste Your Host Where host working your kafka server
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
