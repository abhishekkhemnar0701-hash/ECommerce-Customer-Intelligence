
from sqlalchemy import text
from src.database import engine


def run_quality_checks():

    checks = {
        "Duplicate customers": """
            SELECT COUNT(*) FROM (
                SELECT customer_id
                FROM customers
                GROUP BY customer_id
                HAVING COUNT(*) > 1
            ) x
        """,

        "Orders without customers": """
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c
            ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """,

        "Order items without products": """
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN products p
            ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
        """,

        "Invalid product prices": """
            SELECT COUNT(*)
            FROM products
            WHERE price < 0
        """,

        "Invalid order quantities": """
            SELECT COUNT(*)
            FROM order_items
            WHERE quantity <= 0
        """
    }

    all_passed = True

    with engine.connect() as connection:

        print("\nDATA QUALITY REPORT")

        for check_name, query in checks.items():

            result = connection.execute(
                text(query)
            ).scalar_one()

            status = "PASS" if result == 0 else "FAIL"

            print(
                f"{check_name}: {status} "
                f"(Issues: {result})"
            )

            if result > 0:
                all_passed = False

    print("\nOverall quality:", "PASSED" if all_passed else "FAILED")

    return all_passed


if __name__ == "__main__":
    run_quality_checks()
