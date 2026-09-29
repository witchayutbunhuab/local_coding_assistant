"""
Lab 13: Local Coding Assistant Wrapper
Project: Local_Coding_Assistant
Stack: LangChain + FAISS + Kuzu + Ollama
"""
import pathlib
from hybrid_rag import (
    HybridRAG,
    create_sample_files,
    extract_code_documents,
    build_vectorstore,
    build_graph_db
)

class LocalCodingAssistant:
    def __init__(
        self,
        code_dir: str = "sample_code_12",
        vectorstore_path: str = "vector_store_12",
        graph_db_path: str = "graph_db_12"
    ):
        self.code_dir = code_dir
        self.vectorstore_path = vectorstore_path
        self.graph_db_path = graph_db_path
        self.rag_engine = None
        self._ensure_databases()

    def _ensure_databases(self):
        """ตรวจสอบและสร้างระบบฐานข้อมูล Vector Store และ Graph DB หากยังไม่มีในเครื่อง"""
        if not pathlib.Path(self.code_dir).exists():
            print(f"[Init] Creating sample code in '{self.code_dir}'...")
            create_sample_files(self.code_dir)

        if not pathlib.Path(self.vectorstore_path).exists():
            print(f"[Init] Building Vector Store in '{self.vectorstore_path}'...")
            docs = extract_code_documents(self.code_dir)
            build_vectorstore(docs, self.vectorstore_path)

        if not pathlib.Path(self.graph_db_path).exists():
            print(f"[Init] Building Graph Database in '{self.graph_db_path}'...")
            build_graph_db(self.code_dir, self.graph_db_path)

        print("[Init] Loading Hybrid RAG Engine...")
        self.rag_engine = HybridRAG(self.vectorstore_path, self.graph_db_path)

    def ask(self, question: str, verbose: bool = False) -> dict:
        """รับคำถามและส่งต่อให้ Hybrid RAG Engine ประมวลผล"""
        if not self.rag_engine:
            raise RuntimeError("RAG Engine is not initialized properly.")
        return self.rag_engine.query(question, verbose=verbose)

if __name__ == "__main__":
    # ทดสอบการทำงานผ่าน Terminal/CLI
    assistant = LocalCodingAssistant()
    print("\n=== Local Coding Assistant CLI Test ===")
    
    # 1. ทดสอบ Vector Query (อธิบายการทำงาน)
    q1 = "How does mean function work?"
    print(f"\n[Question 1]: {q1}")
    res1 = assistant.ask(q1, verbose=True)
    print(f"[Answer]:\n{res1['answer']}\n")

    # 2. ทดสอบ Graph Query (วิเคราะห์ความสัมพันธ์)
    q2 = "Who calls mean?"
    print(f"\n[Question 2]: {q2}")
    res2 = assistant.ask(q2, verbose=True)
    print(f"[Answer]:\n{res2['answer']}\n")