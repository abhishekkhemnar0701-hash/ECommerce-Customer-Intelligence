
from pathlib import Path
from src.database import engine

BASE_DIR = Path(__file__).resolve().parents[2]
SQL_FILE = BASE_DIR / "sql" / "create_tables.sql"

sql_script = SQL_FILE.read_text(encoding="utf-8")

connection = engine.raw_connection()

try:
    cursor = connection.cursor()
    cursor.execute(sql_script)
    connection.commit()

    print("All database tables created successfully!")

except Exception as error:
    connection.rollback()
    print("Table creation failed:", error)
    raise

finally:
    cursor.close()
    connection.close()
