
from datetime import datetime
from sqlalchemy import text

from src.database import engine
from src.etl.extract import extract_data
from src.etl.transform import transform_data
from src.etl.load import load_data
from src.etl.data_quality import run_quality_checks


def run_pipeline():

    start_time = datetime.now()

    print("=" * 50)
    print("INCREMENTAL E-COMMERCE ETL PIPELINE")
    print("=" * 50)

    run_id = None

    try:

        with engine.begin() as connection:
            result = connection.execute(
                text("""
                    INSERT INTO pipeline_runs (status)
                    VALUES ('RUNNING')
                    RETURNING run_id
                """)
            )
            run_id = result.scalar_one()

        # EXTRACT
        print("\nSTEP 1: EXTRACT")
        raw_data = extract_data()

        # TRANSFORM
        print("\nSTEP 2: TRANSFORM")
        clean_data = transform_data(raw_data)

        # LOAD
        print("\nSTEP 3: INCREMENTAL LOAD")
        counts = load_data(clean_data)

        # DATA QUALITY
        print("\nSTEP 4: DATA QUALITY")
        quality_passed = run_quality_checks()

        if not quality_passed:
            raise ValueError("Data quality checks failed")

        # RECORD SUCCESS
        with engine.begin() as connection:
            connection.execute(
                text("""
                    UPDATE pipeline_runs
                    SET finished_at = CURRENT_TIMESTAMP,
                        status = 'SUCCESS',
                        customers_processed = :customers,
                        products_processed = :products,
                        orders_processed = :orders,
                        order_items_processed = :items
                    WHERE run_id = :run_id
                """),
                {
                    "customers": counts["customers"],
                    "products": counts["products"],
                    "orders": counts["orders"],
                    "items": counts["order_items"],
                    "run_id": run_id
                }
            )

        print("\nPIPELINE COMPLETED SUCCESSFULLY!")

    except Exception as error:

        if run_id is not None:
            with engine.begin() as connection:
                connection.execute(
                    text("""
                        UPDATE pipeline_runs
                        SET finished_at = CURRENT_TIMESTAMP,
                            status = 'FAILED',
                            error_message = :error
                        WHERE run_id = :run_id
                    """),
                    {
                        "error": str(error)[:4000],
                        "run_id": run_id
                    }
                )

        print("\nPIPELINE FAILED:", error)
        raise

    finally:
        print("Execution time:", datetime.now() - start_time)


if __name__ == "__main__":
    run_pipeline()
