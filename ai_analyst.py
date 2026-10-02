import pyodbc
import pandas as pd
import ollama
import re

from rag import retrieve_context


# ============================================================
# CONFIGURATION
# ============================================================

SERVER = "AXM380"
DATABASE = "ContosoRetailDW"
MODEL = "qwen3:8b"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
    )

    return pyodbc.connect(connection_string)


# ============================================================
# DATABASE SCHEMA
# ============================================================

DATABASE_SCHEMA = """
dbo.FactOnlineSales
- OnlineSalesKey
- DateKey
- StoreKey
- ProductKey
- PromotionKey
- CurrencyKey
- CustomerKey
- SalesOrderNumber
- SalesOrderLineNumber
- SalesQuantity
- SalesAmount
- ReturnQuantity
- ReturnAmount
- DiscountQuantity
- DiscountAmount
- TotalCost
- UnitCost
- UnitPrice

dbo.DimProduct
- ProductKey
- ProductName
- ProductSubcategoryKey
- Manufacturer
- BrandName
- ColorName
- UnitCost
- UnitPrice

dbo.DimProductSubcategory
- ProductSubcategoryKey
- ProductSubcategoryName
- ProductCategoryKey

dbo.DimProductCategory
- ProductCategoryKey
- ProductCategoryName

dbo.DimCustomer
- CustomerKey
- GeographyKey
- FirstName
- LastName
- Gender
- YearlyIncome
- Education
- Occupation
- CustomerType
- CompanyName

dbo.DimStore
- StoreKey
- GeographyKey
- StoreType
- StoreName

dbo.DimGeography
- GeographyKey
- ContinentName
- CityName
- StateProvinceName
- RegionCountryName

dbo.DimDate
- Datekey
- CalendarYear
- CalendarQuarter
- CalendarMonth
- CalendarMonthLabel
- FiscalYear
- FiscalQuarter
- FiscalMonth
"""


# ============================================================
# GENERATE SQL USING RAG + QWEN
# ============================================================

def generate_sql(question):

    # Retrieve only the relevant knowledge for this question
    rag_context = retrieve_context(question)

    prompt = f"""
You are an expert Microsoft SQL Server data analyst.

Convert the user's business question into one SQL Server SELECT query.

RETRIEVED CONTEXT FROM RAG:

{rag_context}

DATABASE SCHEMA:

{DATABASE_SCHEMA}

IMPORTANT RULES:

1. Use ONLY tables and columns from the provided database schema.

2. Use the retrieved RAG context to understand:
   - table relationships
   - business definitions
   - formulas

3. Generate Microsoft SQL Server syntax only.

4. Only SELECT statements are allowed.

5. Never use:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   TRUNCATE
   CREATE
   EXEC
   MERGE

6. Never invent tables or columns.

7. Use proper JOIN conditions using the provided relationships.

8. Sales revenue means:
   SUM(FactOnlineSales.SalesAmount)

9. If profit is requested, use:
   SUM(FactOnlineSales.SalesAmount)
   - SUM(FactOnlineSales.TotalCost)

10. If profit margin is requested, use:
    (
        SUM(FactOnlineSales.SalesAmount)
        - SUM(FactOnlineSales.TotalCost)
    )
    / NULLIF(SUM(FactOnlineSales.SalesAmount), 0)

11. IMPORTANT SQL SERVER RULE:
    TOP must always appear immediately after SELECT.

    CORRECT:
    SELECT TOP 5 ProductName
    FROM dbo.DimProduct
    ORDER BY ProductName;

    WRONG:
    SELECT ProductName
    FROM dbo.DimProduct
    ORDER BY ProductName
    TOP 5;

12. Do not use LIMIT because this is SQL Server.

13. Return ONLY the SQL query.

14. Do not use markdown code blocks.

15. Do not explain the query.

USER QUESTION:

{question}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# ============================================================
# CLEAN GENERATED SQL
# ============================================================

def clean_sql(sql):

    # Remove possible markdown formatting
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    # Remove possible Qwen thinking output
    sql = re.sub(
        r"<think>.*?</think>",
        "",
        sql,
        flags=re.DOTALL
    )

    return sql.strip()


# ============================================================
# SQL SAFETY VALIDATION
# ============================================================

def validate_sql(sql):

    forbidden_commands = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "EXEC",
        "MERGE"
    ]

    sql_upper = sql.upper().strip()

    # Only SELECT is allowed
    if not sql_upper.startswith("SELECT"):
        return False

    # Block dangerous commands
    for command in forbidden_commands:

        if re.search(
            rf"\b{command}\b",
            sql_upper
        ):
            return False

    return True


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    conn = get_connection()

    try:

        df = pd.read_sql(
            sql,
            conn
        )

        return df

    finally:

        conn.close()


# ============================================================
# OPTIONAL AI SUMMARY
# ============================================================

def explain_results(question, results):

    # Send maximum 30 rows to the LLM
    data = results.head(30).to_string(
        index=False
    )

    prompt = f"""
You are a business data analyst.

The user asked:

{question}

The SQL Server database returned the following data:

{data}

Explain the result in a short and clear business-friendly summary.

IMPORTANT RULES:

1. Only use information contained in the supplied result.

2. Do not invent facts.

3. Do not invent reasons or causes.

4. Mention the most important values.

5. Keep the answer concise.

6. Never assume a currency unless currency information
   is explicitly included in the supplied result.

7. Do not claim that something caused an increase or decrease
   unless the supplied result supports that conclusion.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI DATA ANALYST - CONTOSO")
    print("=" * 60)

    question = input(
        "\nAsk a question about your data:\n> "
    )

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    print("\nRetrieving relevant context...")

    context = retrieve_context(question)

    print("\nRAG Context:")
    print("-" * 60)
    print(context)
    print("-" * 60)

    # --------------------------------------------------------
    # GENERATE SQL
    # --------------------------------------------------------

    print("\nGenerating SQL with Qwen...")

    sql = generate_sql(question)
    sql = clean_sql(sql)

    print("\nGenerated SQL:")
    print("-" * 60)
    print(sql)
    print("-" * 60)

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not validate_sql(sql):

        print("\nUnsafe or invalid SQL generated.")
        exit()

    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    print("\nExecuting SQL...")

    try:

        results = execute_sql(sql)

    except Exception as error:

        print("\nSQL execution failed:")
        print(error)

        print(
            "\nPlease try the question again "
            "or rephrase it."
        )

        exit()

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if results.empty:

        print("\nThe query returned no data.")
        exit()

    print("\nDatabase Result:")
    print("-" * 60)

    print(
        results.head(20).to_string(
            index=False
        )
    )

    print("-" * 60)