KNOWLEDGE_BASE = [
    {
        "keywords": ["sales", "revenue", "online sales"],
        "content": """
FactOnlineSales contains online sales transactions.

Important columns:
- ProductKey
- CustomerKey
- StoreKey
- DateKey
- SalesQuantity
- SalesAmount
- ReturnAmount
- TotalCost

Business rule:
Revenue = SUM(FactOnlineSales.SalesAmount)
"""
    },

    {
        "keywords": ["product", "products", "brand", "manufacturer"],
        "content": """
DimProduct contains product information.

Important columns:
- ProductKey
- ProductName
- ProductSubcategoryKey
- Manufacturer
- BrandName
- ColorName
- UnitCost
- UnitPrice

Relationship:
FactOnlineSales.ProductKey = DimProduct.ProductKey
"""
    },

    {
        "keywords": ["category", "categories", "subcategory"],
        "content": """
Product hierarchy:

DimProduct.ProductSubcategoryKey =
DimProductSubcategory.ProductSubcategoryKey

DimProductSubcategory.ProductCategoryKey =
DimProductCategory.ProductCategoryKey

Hierarchy:
Category -> Subcategory -> Product
"""
    },

    {
        "keywords": ["customer", "customers", "gender", "income", "occupation"],
        "content": """
DimCustomer contains customer information.

Important columns:
- CustomerKey
- GeographyKey
- FirstName
- LastName
- Gender
- YearlyIncome
- Education
- Occupation
- CustomerType

Relationship:
FactOnlineSales.CustomerKey = DimCustomer.CustomerKey
"""
    },

    {
        "keywords": ["country", "city", "region", "geography", "location"],
        "content": """
DimGeography contains geographical information.

Important columns:
- GeographyKey
- ContinentName
- CityName
- StateProvinceName
- RegionCountryName

Relationships:
DimCustomer.GeographyKey = DimGeography.GeographyKey
DimStore.GeographyKey = DimGeography.GeographyKey
"""
    },

    {
        "keywords": ["store", "stores"],
        "content": """
DimStore contains store information.

Important columns:
- StoreKey
- GeographyKey
- StoreType
- StoreName

Relationship:
FactOnlineSales.StoreKey = DimStore.StoreKey
"""
    },

    {
        "keywords": [
            "year", "month", "quarter", "date",
            "yearly", "monthly", "trend"
        ],
        "content": """
DimDate contains calendar information.

Important columns:
- Datekey
- CalendarYear
- CalendarQuarter
- CalendarMonth
- CalendarMonthLabel
- FiscalYear
- FiscalQuarter
- FiscalMonth

Relationship:
FactOnlineSales.DateKey = DimDate.Datekey
"""
    },

    {
        "keywords": ["profit", "margin", "cost"],
        "content": """
Business rules:

Revenue = SUM(SalesAmount)

Cost = SUM(TotalCost)

Profit = SUM(SalesAmount) - SUM(TotalCost)

Profit Margin =
(SUM(SalesAmount) - SUM(TotalCost))
/ NULLIF(SUM(SalesAmount), 0)
"""
    },

    {
        "keywords": ["return", "returns", "returned"],
        "content": """
FactOnlineSales contains return information.

ReturnQuantity represents returned quantity.

ReturnAmount represents the monetary amount associated with returns.
"""
    }
]