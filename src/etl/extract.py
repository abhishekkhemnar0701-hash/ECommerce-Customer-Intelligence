
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"

def extract_data():

    files = {
        "customers": "customers.csv",
        "products": "products.csv",
        "orders": "orders.csv",
        "order_items": "order_items.csv"
    }

    extracted_data = {}

    for table_name, filename in files.items():

        file_path = RAW_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        df = pd.read_csv(file_path)

        extracted_data[table_name] = df

        print(
            f"Extracted {table_name}: {len(df)} records"
        )

    return extracted_data


if __name__ == "__main__":
    data = extract_data()
    print("Data extraction completed successfully!")
