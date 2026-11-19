
import json
import random
import time
import uuid
from datetime import datetime, timezone

from kafka import KafkaProducer
from sqlalchemy import text

from src.database import engine


BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "ecommerce_orders"


def get_source_data():

    with engine.connect() as connection:

        customers = connection.execute(
            text("SELECT customer_id FROM customers")
        ).scalars().all()

        products = connection.execute(
            text("SELECT product_id, price FROM products")
        ).fetchall()

    if not customers or not products:
        raise ValueError("Customers or products table is empty")

    return customers, products


def create_producer():

    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks="all",
        retries=5
    )


def generate_order(customers, products):

    customer_id = random.choice(customers)
    product = random.choice(products)

    quantity = random.randint(1, 3)
    unit_price = float(product.price)

    total_amount = round(quantity * unit_price, 2)

    event = {
        "event_id": str(uuid.uuid4()),
        "order_id": str(uuid.uuid4()),
        "customer_id": int(customer_id),
        "product_id": int(product.product_id),
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total_amount,
        "payment_method": random.choice(
            ["UPI", "Credit Card", "Debit Card", "COD"]
        ),
        "order_status": "Processing",
        "event_timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

    return event


def run_producer(count=10):

    customers, products = get_source_data()

    producer = create_producer()

    try:
        print("Kafka producer started!")
        print(f"Generating {count} order events...\n")

        for number in range(1, count + 1):

            event = generate_order(customers, products)

            future = producer.send(
                TOPIC,
                value=event,
                key=event["order_id"].encode("utf-8")
            )

            metadata = future.get(timeout=30)

            print(
                f"Event {number}/{count} sent | "
                f"Order ID: {event['order_id']} | "
                f"Partition: {metadata.partition} | "
                f"Offset: {metadata.offset}"
            )

            time.sleep(2)

        producer.flush()
        print("\nAll order events sent successfully!")

    finally:
        producer.close()


if __name__ == "__main__":
    run_producer(count=10)
