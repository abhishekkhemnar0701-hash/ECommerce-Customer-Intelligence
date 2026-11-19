
import pandas as pd

def transform_data(data):

    customers = data["customers"].copy()
    products = data["products"].copy()
    orders = data["orders"].copy()
    order_items = data["order_items"].copy()

    # 1. Clean customers
    customers = customers.drop_duplicates(
        subset=["customer_id"]
    )

    customers["customer_name"] = (
        customers["customer_name"].fillna("").str.strip()
    )

    customers["email"] = (
        customers["email"].fillna("").str.strip().str.lower()
    )

    customers["city"] = customers["city"].fillna("Unknown")
    customers["state"] = customers["state"].fillna("Unknown")

    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"], errors="coerce"
    ).dt.date

    customers = customers[
        (customers["customer_id"] > 0) &
        (customers["customer_name"] != "") &
        (customers["email"] != "") &
        (customers["signup_date"].notna())
    ]

    customers = customers.drop_duplicates(subset=["email"])

    # 2. Clean products
    products = products.drop_duplicates(
        subset=["product_id"]
    )

    products["product_name"] = (
        products["product_name"].fillna("").str.strip()
    )

    products["category"] = (
        products["category"].fillna("Unknown").str.strip()
    )

    products["price"] = pd.to_numeric(
        products["price"], errors="coerce"
    )

    products["stock_quantity"] = pd.to_numeric(
        products["stock_quantity"], errors="coerce"
    )

    products = products[
        (products["product_id"] > 0) &
        (products["product_name"] != "") &
        (products["price"].notna()) &
        (products["price"] >= 0) &
        (products["stock_quantity"].notna()) &
        (products["stock_quantity"] >= 0)
    ]

    products["stock_quantity"] = (
        products["stock_quantity"].astype(int)
    )

    # 3. Clean orders
    orders = orders.drop_duplicates(
        subset=["order_id"]
    )

    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    )

    orders["total_amount"] = pd.to_numeric(
        orders["total_amount"], errors="coerce"
    )

    orders["payment_method"] = (
        orders["payment_method"].fillna("Unknown")
    )

    orders["order_status"] = (
        orders["order_status"].fillna("Unknown")
    )

    valid_customer_ids = set(customers["customer_id"])

    orders = orders[
        (orders["order_id"] > 0) &
        (orders["customer_id"].isin(valid_customer_ids)) &
        (orders["order_date"].notna()) &
        (orders["total_amount"].notna()) &
        (orders["total_amount"] >= 0)
    ]

    # 4. Clean order items
    order_items = order_items.drop_duplicates(
        subset=["order_item_id"]
    )

    for column in ["quantity", "unit_price", "item_total"]:
        order_items[column] = pd.to_numeric(
            order_items[column], errors="coerce"
        )

    valid_order_ids = set(orders["order_id"])
    valid_product_ids = set(products["product_id"])

    order_items = order_items[
        (order_items["order_item_id"] > 0) &
        (order_items["order_id"].isin(valid_order_ids)) &
        (order_items["product_id"].isin(valid_product_ids)) &
        (order_items["quantity"].notna()) &
        (order_items["quantity"] > 0) &
        (order_items["unit_price"].notna()) &
        (order_items["unit_price"] >= 0) &
        (order_items["item_total"].notna()) &
        (order_items["item_total"] >= 0)
    ]

    # Recalculate item totals to ensure consistency
    order_items["item_total"] = (
        order_items["quantity"] * order_items["unit_price"]
    ).round(2)

    order_items["quantity"] = (
        order_items["quantity"].astype(int)
    )

    # Return cleaned datasets
    cleaned_data = {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items
    }

    print("\nTRANSFORMATION SUMMARY")

    for name, df in cleaned_data.items():
        print(f"{name}: {len(df)} clean records")

    print("\nData transformation completed!")

    return cleaned_data


if __name__ == "__main__":
    from src.etl.extract import extract_data

    raw_data = extract_data()
    clean_data = transform_data(raw_data)
