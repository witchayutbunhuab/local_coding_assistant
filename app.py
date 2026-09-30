"""
Lab 13: Local_Coding_Assistant — Streamlit Web UI
Run with: uv run streamlit run lab_13_app.py
"""
import pathlib
import streamlit as st
from coding_assistant import LocalCodingAssistant

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Local_Coding_Assistant",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Local_Coding_Assistant (Hybrid RAG: Vector + Graph)")

# ─── System Initialization ───────────────────────────────────────────────────
@st.cache_resource
def get_assistant():
    return LocalCodingAssistant(
        code_dir="witchayut_Local_Coding_Assistant_Dataset",
        vectorstore_path="vector_store_12",
        graph_db_path="graph_db_12"
    )

try:
    assistant = get_assistant()
    st.sidebar.success("✅ System Status: Hybrid RAG Engine Ready")
except Exception as e:
    st.sidebar.error(f"❌ Error loading RAG Engine: {e}")
    st.stop()

# ─── Sidebar Controls & Information ──────────────────────────────────────────
st.sidebar.header("⚙️ Controls")

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Example Questions")

st.sidebar.markdown("**Vector Mode (Code Understanding):**")
st.sidebar.caption("• How does the mean function work?")
st.sidebar.caption("• Explain the logic of factorial function.")

st.sidebar.markdown("**Graph Mode (Call Relationships):**")
st.sidebar.caption("• Who calls mean?")
st.sidebar.caption("• What functions does run_pipeline call?")

# ─── Chat History Initialization ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Render Existing Chat History ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "metadata" in msg:
            meta = msg["metadata"]
            st.info(f"**Mode Used:** `{meta.get('source', '').upper()}` | **Reason:** {meta.get('reason')}")
            with st.expander("🔍 View Retrieved Sources / Graph Data"):
                if meta.get("source") == "vector":
                    st.json(meta.get("retrieved_docs", []))
                else:
                    st.json(meta.get("graph_context", []))

# ─── Handle User Prompt ───────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about the code..."):
    # Display user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing codebase with Hybrid RAG..."):
            res = assistant.ask(prompt, verbose=True)
            answer = res.get("answer", "No response generated.")

            st.write(answer)
            st.info(f"**Mode Used:** `{res.get('source', '').upper()}` | **Reason:** {res.get('reason')}")

            with st.expander("🔍 View Retrieved Sources / Graph Data"):
                if res.get("source") == "vector":
                    st.json(res.get("retrieved_docs", []))
                else:
                    st.json(res.get("graph_context", []))

    # Save response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "metadata": res
    })