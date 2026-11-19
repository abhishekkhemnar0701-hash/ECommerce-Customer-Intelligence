
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

def save_csv(filename, records):
    path = RAW_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print(f"Generated: {path}")

# 1. Generate customers
customers = []

for customer_id in range(1, 501):
    customers.append({
        "customer_id": customer_id,
        "customer_name": fake.name(),
        "email": fake.unique.email(),
        "city": fake.city(),
        "state": fake.state(),
        "signup_date": fake.date_between(
            start_date="-3y", end_date="today"
        ).isoformat()
    })

# 2. Generate products
categories = [
    "Electronics", "Fashion", "Home",
    "Beauty", "Sports", "Books"
]

products = []

for product_id in range(1, 101):
    products.append({
        "product_id": product_id,
        "product_name": fake.catch_phrase(),
        "category": random.choice(categories),
        "price": round(random.uniform(100, 50000), 2),
        "stock_quantity": random.randint(0, 500)
    })

# 3. Generate orders
orders = []
order_items = []

payment_methods = ["UPI", "Credit Card", "Debit Card", "COD", "Net Banking"]
statuses = ["Delivered", "Shipped", "Processing", "Cancelled"]

start_date = datetime.now() - timedelta(days=365)

for order_id in range(1, 2001):
    customer_id = random.randint(1, 500)
    order_date = start_date + timedelta(
        seconds=random.randint(0, 365 * 24 * 60 * 60)
    )

    order_total = 0

    selected_products = random.sample(products, random.randint(1, 4))

    for product in selected_products:
        quantity = random.randint(1, 3)
        item_total = round(product["price"] * quantity, 2)
        order_total += item_total

        order_items.append({
            "order_item_id": len(order_items) + 1,
            "order_id": order_id,
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": product["price"],
            "item_total": item_total
        })

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "total_amount": round(order_total, 2),
        "payment_method": random.choice(payment_methods),
        "order_status": random.choice(statuses)
    })

# 4. Save datasets
save_csv("customers.csv", customers)
save_csv("products.csv", products)
save_csv("orders.csv", orders)
save_csv("order_items.csv", order_items)

print("\nAll e-commerce datasets generated successfully!")
print(f"Customers: {len(customers)}")
print(f"Products: {len(products)}")
print(f"Orders: {len(orders)}")
print(f"Order items: {len(order_items)}")
