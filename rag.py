from knowledge_base import KNOWLEDGE_BASE


def retrieve_context(question, max_results=4):

    question_lower = question.lower()

    matches = []

    for item in KNOWLEDGE_BASE:

        score = 0

        for keyword in item["keywords"]:
            if keyword in question_lower:
                score += 1

        if score > 0:
            matches.append(
                (score, item["content"])
            )

    matches.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = matches[:max_results]

    if not selected:
        return """
General database context:

FactOnlineSales contains online sales transactions.
SalesAmount represents sales revenue.

FactOnlineSales.ProductKey = DimProduct.ProductKey.
FactOnlineSales.CustomerKey = DimCustomer.CustomerKey.
FactOnlineSales.StoreKey = DimStore.StoreKey.
FactOnlineSales.DateKey = DimDate.Datekey.
"""

    return "\n\n".join(
        content for score, content in selected
    )



if __name__ == "__main__":

    question = input("Ask a question: ")

    context = retrieve_context(question)

    print("\nRetrieved RAG context:")
    print("=" * 60)
    print(context)