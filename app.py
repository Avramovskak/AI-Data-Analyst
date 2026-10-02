import streamlit as st

from ai_analyst import (
    generate_sql,
    clean_sql,
    validate_sql,
    execute_sql,
    explain_results
)

from rag import retrieve_context


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "results" not in st.session_state:
    st.session_state.results = None

if "sql" not in st.session_state:
    st.session_state.sql = None

if "question" not in st.session_state:
    st.session_state.question = None

if "rag_context" not in st.session_state:
    st.session_state.rag_context = None

if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI Data Analyst")

st.write(
    "Ask business questions about the ContosoRetailDW database "
    "using natural language."
)

st.caption(
    "Powered by RAG, Qwen3 and Microsoft SQL Server"
)


# ============================================================
# QUESTION INPUT
# ============================================================

question = st.text_input(
    "What would you like to know?",
    placeholder=(
        "Example: Show me the top 5 "
        "product categories by profit"
    )
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "Analyze",
    type="primary"
):

    if not question:

        st.warning(
            "Please enter a question."
        )

    else:

        # Reset previous result
        st.session_state.results = None
        st.session_state.sql = None
        st.session_state.ai_summary = None
        st.session_state.question = question

        try:

            # =================================================
            # STEP 1 - RAG
            # =================================================

            with st.spinner(
                "Retrieving relevant context..."
            ):

                rag_context = retrieve_context(
                    question
                )

                st.session_state.rag_context = (
                    rag_context
                )


            # =================================================
            # STEP 2 - GENERATE SQL
            # =================================================

            with st.spinner(
                "Qwen is generating SQL..."
            ):

                sql = generate_sql(
                    question
                )

                sql = clean_sql(
                    sql
                )

                st.session_state.sql = sql


            # =================================================
            # STEP 3 - SECURITY CHECK
            # =================================================

            if not validate_sql(sql):

                st.error(
                    "The generated SQL query "
                    "did not pass the safety check."
                )

                st.stop()


            # =================================================
            # STEP 4 - EXECUTE SQL
            # =================================================

            with st.spinner(
                "Querying ContosoRetailDW..."
            ):

                results = execute_sql(
                    sql
                )


            if results.empty:

                st.warning(
                    "The query returned no data."
                )

            else:

                st.session_state.results = results


        except Exception as error:

            st.error(
                "The generated SQL query could not be executed."
            )

            st.code(
                str(error)
            )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.results is not None:

    results = st.session_state.results


    # ========================================================
    # RESULTS TABLE
    # ========================================================

    st.divider()

    st.subheader("📊 Query Results")

    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # AUTOMATIC VISUALIZATION
    # ========================================================

    numeric_columns = (
        results.select_dtypes(
            include="number"
        ).columns.tolist()
    )

    text_columns = (
        results.select_dtypes(
            exclude="number"
        ).columns.tolist()
    )


    if (
        len(numeric_columns) > 0
        and len(text_columns) > 0
        and len(results) <= 30
    ):

        st.subheader(
            "📈 Visualization"
        )

        try:

            chart_data = results[
                [
                    text_columns[0],
                    numeric_columns[0]
                ]
            ].copy()

            chart_data = chart_data.set_index(
                text_columns[0]
            )

            st.bar_chart(
                chart_data
            )

        except Exception:

            pass


    # ========================================================
    # OPTIONAL AI SUMMARY
    # ========================================================

    st.subheader("🤖 AI Summary")

    st.caption(
        "Optional — generating a summary uses Qwen again "
        "and may take additional time."
    )


    if st.button(
        "Generate AI Summary"
    ):

        with st.spinner(
            "Qwen is analyzing the result..."
        ):

            try:

                summary = explain_results(
                    st.session_state.question,
                    results
                )

                st.session_state.ai_summary = (
                    summary
                )

            except Exception as error:

                st.error(
                    "AI summary could not be generated."
                )

                st.code(
                    str(error)
                )


    if st.session_state.ai_summary:

        st.info(
            st.session_state.ai_summary
        )


# ============================================================
# GENERATED SQL
# ============================================================

if st.session_state.sql:

    with st.expander(
        "🔍 Generated SQL"
    ):

        st.code(
            st.session_state.sql,
            language="sql"
        )


# ============================================================
# RAG CONTEXT
# ============================================================

if st.session_state.rag_context:

    with st.expander(
        "📚 Retrieved RAG Context"
    ):

        st.text(
            st.session_state.rag_context
        )


# ============================================================
# HOW IT WORKS
# ============================================================

with st.expander(
    "ℹ️ How does this system work?"
):

    st.markdown(
        """
**1. Natural Language Question**  
The user asks a business question.

**2. RAG Retrieval**  
The system retrieves relevant database relationships
and business rules from the knowledge base.

**3. Qwen3**  
The local language model converts the question and
retrieved context into Microsoft SQL Server SQL.

**4. SQL Safety Check**  
Only read-only SELECT queries are allowed.

**5. SQL Server**  
The query is executed against the ContosoRetailDW database.

**6. Visualization**  
The result is displayed as a table and, when possible,
as a chart.

**7. Optional AI Summary**  
The user can choose to send the result to Qwen again
for a natural-language explanation.
"""
    )