
import pandas as pd
from sqlalchemy import text

from src.database import engine


def calculate_score(series, reverse=False):

    ranks = series.rank(method="first", pct=True)

    scores = pd.cut(
        ranks,
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True
    ).astype(int)

    if reverse:
        scores = 6 - scores

    return scores


def get_customer_data():

    query = """
        WITH all_orders AS (

            SELECT
                customer_id,
                order_id::TEXT AS order_id,
                order_date AS purchase_date,
                total_amount AS amount
            FROM orders
            WHERE LOWER(COALESCE(order_status, ''))
                  <> 'cancelled'

            UNION ALL

            SELECT
                customer_id,
                order_id::TEXT AS order_id,
                event_timestamp AS purchase_date,
                total_amount AS amount
            FROM streaming_order_events
            WHERE LOWER(COALESCE(order_status, ''))
                  <> 'cancelled'
        )

        SELECT
            c.customer_id,
            MAX(o.purchase_date) AS last_purchase_date,
            COUNT(DISTINCT o.order_id) AS frequency,
            COALESCE(SUM(o.amount), 0) AS monetary

        FROM customers c

        LEFT JOIN all_orders o
            ON c.customer_id = o.customer_id

        GROUP BY c.customer_id
    """

    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)

    return df


def assign_segment(row):

    if row["frequency"] == 0:
        return "No Purchase Yet"

    r = row["recency_score"]
    f = row["frequency_score"]
    m = row["monetary_score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"

    elif r <= 2 and f >= 4 and m >= 4:
        return "Cannot Lose Them"

    elif f >= 4 and m >= 3:
        return "Loyal Customers"

    elif r >= 4 and f >= 2:
        return "Potential Loyalists"

    elif r >= 4 and f == 1:
        return "New Customers"

    elif r <= 2 and f >= 3:
        return "At Risk"

    elif r <= 2 and f <= 2:
        return "Hibernating"

    return "Need Attention"


def run_rfm_analysis():

    print("Starting customer intelligence analysis...")

    df = get_customer_data()

    df["last_purchase_date"] = pd.to_datetime(
        df["last_purchase_date"], utc=True, errors="coerce"
    )

    current_time = pd.Timestamp.now(tz="UTC")

    df["recency_days"] = (
        current_time - df["last_purchase_date"]
    ).dt.days

    df["frequency"] = df["frequency"].fillna(0).astype(int)

    df["monetary"] = pd.to_numeric(
        df["monetary"], errors="coerce"
    ).fillna(0).round(2)

    # Customers without purchases receive the lowest scores
    # and are classified separately.
    active = df["frequency"] > 0

    df["recency_score"] = 1
    df["frequency_score"] = 1
    df["monetary_score"] = 1

    if active.sum() > 0:

        df.loc[active, "recency_score"] = calculate_score(
            df.loc[active, "recency_days"],
            reverse=True
        )

        df.loc[active, "frequency_score"] = calculate_score(
            df.loc[active, "frequency"]
        )

        df.loc[active, "monetary_score"] = calculate_score(
            df.loc[active, "monetary"]
        )

    for column in [
        "recency_score",
        "frequency_score",
        "monetary_score"
    ]:
        df[column] = df[column].astype(int)

    df["rfm_score"] = (
        df["recency_score"].astype(str)
        + df["frequency_score"].astype(str)
        + df["monetary_score"].astype(str)
    )

    df["customer_segment"] = df.apply(
        assign_segment, axis=1
    )

    # Save the latest customer intelligence snapshot
    with engine.begin() as connection:

        connection.execute(
            text("DELETE FROM customer_rfm")
        )

        df.to_sql(
            "customer_rfm",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=500
        )

    print("\nCUSTOMER SEGMENTATION RESULTS")

    print(
        df["customer_segment"].value_counts().to_string()
    )

    print("\nRFM analysis completed successfully!")

    return df


if __name__ == "__main__":
    run_rfm_analysis()
