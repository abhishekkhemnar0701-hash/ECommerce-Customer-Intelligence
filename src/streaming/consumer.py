
import json
from datetime import datetime

from kafka import KafkaConsumer
from sqlalchemy import text

from src.database import engine


BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "ecommerce_orders"


def validate_event(event):

    required_fields = [
        "event_id",
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "event_timestamp"
    ]

    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing field: {field}")

    if int(event["quantity"]) <= 0:
        raise ValueError("Invalid order quantity")

    if float(event["unit_price"]) < 0:
        raise ValueError("Invalid unit price")

    if float(event["total_amount"]) < 0:
        raise ValueError("Invalid total amount")

    expected_total = round(
        int(event["quantity"]) * float(event["unit_price"]), 2
    )

    if round(float(event["total_amount"]), 2) != expected_total:
        raise ValueError("Order total does not match quantity and price")


def save_to_postgres(event):

    validate_event(event)

    event_timestamp = datetime.fromisoformat(
        event["event_timestamp"].replace("Z", "+00:00")
    )

    query = text("""
        INSERT INTO streaming_order_events (
            event_id,
            order_id,
            customer_id,
            product_id,
            quantity,
            unit_price,
            total_amount,
            payment_method,
            order_status,
            event_timestamp
        )
        VALUES (
            :event_id,
            :order_id,
            :customer_id,
            :product_id,
            :quantity,
            :unit_price,
            :total_amount,
            :payment_method,
            :order_status,
            :event_timestamp
        )
        ON CONFLICT DO NOTHING
    """)

    with engine.begin() as connection:

        result = connection.execute(
            query,
            {
                **event,
                "event_timestamp": event_timestamp
            }
        )

    if result.rowcount == 1:
        print(
            f"Saved order {event['order_id']} to PostgreSQL"
        )
    else:
        print(
            f"Duplicate event ignored: {event['event_id']}"
        )


def run_consumer():

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="ecommerce-order-consumer-v1",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        )
    )

    print("Kafka consumer started!")
    print(f"Listening to topic: {TOPIC}")

    try:

        for message in consumer:

            event = message.value

            print("\nReceived new order event:")
            print(json.dumps(event, indent=4))

            # Save first, commit Kafka offset second.
            save_to_postgres(event)

            consumer.commit()

            print("Kafka offset committed successfully!")

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")

    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
