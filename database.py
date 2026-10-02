import pyodbc
import pandas as pd

SERVER = "AXM380"
DATABASE = "ContosoRetailDW"

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

print("Connecting to SQL Server...")

conn = pyodbc.connect(connection_string)

print("Connected successfully!")

query = """
SELECT TOP 10 *
FROM dbo.FactOnlineSales
"""

df = pd.read_sql(query, conn)

print("\nData from Contoso:")
print(df)

conn.close()