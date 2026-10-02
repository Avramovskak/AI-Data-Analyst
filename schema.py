import pyodbc

SERVER = "AXM380"
DATABASE = "ContosoRetailDW"

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

query = """
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN (
    'FactOnlineSales',
    'DimProduct',
    'DimProductCategory',
    'DimProductSubcategory',
    'DimCustomer',
    'DimDate',
    'DimStore',
    'DimGeography'
)
ORDER BY TABLE_NAME, ORDINAL_POSITION;
"""

cursor.execute(query)

current_table = None

for row in cursor.fetchall():

    table = f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}"

    if table != current_table:
        print(f"\n{table}")
        print("-" * 40)
        current_table = table

    print(f"{row.COLUMN_NAME} ({row.DATA_TYPE})")

conn.close()