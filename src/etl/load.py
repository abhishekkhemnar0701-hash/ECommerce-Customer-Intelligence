
import pandas as pd
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert
from src.database import engine


def load_data(data):

    load_order = [
        "customers",
        "products",
        "orders",
        "order_items"
    ]

    processed_counts = {}

    with engine.begin() as connection:

        metadata = MetaData()

        for table_name in load_order:

            df = data[table_name].copy()

            # Convert missing values to SQL NULL
            df = df.astype(object).where(
                pd.notna(df), None
            )

            records = df.to_dict(orient="records")

            table = Table(
                table_name,
                metadata,
                autoload_with=connection
            )

            primary_keys = [
                column.name
                for column in table.primary_key.columns
            ]

            update_columns = [
                column.name
                for column in table.columns
                if column.name not in primary_keys
            ]

            for start in range(0, len(records), 500):

                batch = records[start:start + 500]

                if not batch:
                    continue

                statement = insert(table).values(batch)

                statement = statement.on_conflict_do_update(
                    index_elements=primary_keys,
                    set_={
                        column: statement.excluded[column]
                        for column in update_columns
                    }
                )

                connection.execute(statement)

            processed_counts[table_name] = len(records)

            print(
                f"Incrementally loaded {len(records)} "
                f"records into {table_name}"
            )

    print("\nIncremental loading completed!")

    return processed_counts
