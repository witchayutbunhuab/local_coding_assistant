"""
Lab 12: Hybrid RAG Engine — Vector + Graph (Completed Version)
Stack: LangChain + FAISS + Kuzu + Ollama
"""
import ast
import io
import pathlib
import shutil
import sys
from typing import Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
import kuzu

# ─── Sample Code Setup ────────────────────────────────────────────────────────
MATH_PY = '''
"""Math utility functions."""
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    result = add(a, 0)
    return result + a * (b - 1)

def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''

STATS_PY = '''
"""Statistical analysis functions."""
from typing import List
import math

def mean(numbers: List[float]) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def variance(numbers: List[float]) -> float:
    m = mean(numbers)
    return sum((x - m) ** 2 for x in numbers) / len(numbers)

def std_dev(numbers: List[float]) -> float:
    return math.sqrt(variance(numbers))
'''

PIPELINE_PY = '''
"""Data processing pipeline."""
from typing import List

def load_data(source: str) -> List[float]:
    return [1.0, 2.0, 3.0, 4.0, 5.0]

def preprocess(data: List[float]) -> List[float]:
    return [x for x in data if x >= 0]

def run_pipeline(source: str) -> dict:
    data = load_data(source)
    processed = preprocess(data)
    return {"count": len(processed), "data": processed}
'''

def create_sample_files(base_dir: str = "sample_code_12") -> list[str]:
    base_path = pathlib.Path(base_dir)
    base_path.mkdir(exist_ok=True)
    files = {"math_utils.py": MATH_PY, "stats.py": STATS_PY, "pipeline.py": PIPELINE_PY}
    created = []
    for name, content in files.items():
        p = base_path / name
        p.write_text(content, encoding="utf-8")
        created.append(str(p))
    return created

def extract_code_documents(directory: str) -> list:
    from langchain_core.documents import Document
    docs = []
    for py_file in pathlib.Path(directory).rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = source.split("\n")[node.lineno - 1: node.end_lineno]
                docs.append(Document(
                    page_content="\n".join(lines),
                    metadata={"function": node.name, "file": str(py_file), "line": node.lineno}
                ))
    return docs

def build_vectorstore(docs: list, save_path: str = "vector_store_12"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(save_path)
    return vs

def build_graph_db(directory: str, db_path: str = "graph_db_12"):
    if pathlib.Path(db_path).exists():
        shutil.rmtree(db_path)

    db = kuzu.Database(db_path)
    conn = kuzu.Connection(db)

    conn.execute("CREATE NODE TABLE IF NOT EXISTS Function (name STRING, file STRING, line INT64, PRIMARY KEY (name))")
    conn.execute("CREATE NODE TABLE IF NOT EXISTS Module (name STRING, filepath STRING, PRIMARY KEY (name))")
    conn.execute("CREATE REL TABLE IF NOT EXISTS CALLS (FROM Function TO Function)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS DEFINED_IN (FROM Function TO Module)")

    for py_file in pathlib.Path(directory).rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        module_name = str(py_file).replace("\\", "/").replace(".py", "")
        conn.execute("MERGE (:Module {name: $n, filepath: $fp})", {"n": module_name, "fp": str(py_file)})
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fk = f"{module_name}.{node.name}"
                conn.execute("MERGE (:Function {name: $n, file: $f, line: $l})", {"n": fk, "f": str(py_file), "l": node.lineno})
                conn.execute("MATCH (f:Function),(m:Module) WHERE f.name=$fn AND m.name=$mn MERGE (f)-[:DEFINED_IN]->(m)", {"fn": fk, "mn": module_name})
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        cid = None
                        if isinstance(child.func, ast.Name): cid = child.func.id
                        elif isinstance(child.func, ast.Attribute): cid = child.func.attr
                        if cid:
                            conn.execute("MERGE (:Function {name: $n, file: '', line: 0})", {"n": cid})
                            conn.execute("MATCH (a:Function),(b:Function) WHERE a.name=$a AND b.name=$b MERGE (a)-[:CALLS]->(b)", {"a": fk, "b": cid})
    return conn

# ─── TODO 1: QuestionRouter ──────────────────────────────────────────────────
class QuestionRouter:
    GRAPH_KEYWORDS = [
        "calls", "called", "call", "imports", "import", "depends", "depend",
        "relationship", "structure", "caller", "callee", "defined in", "impact"
    ]

    def classify(self, question: str) -> str:
        q_lower = question.lower()
        for kw in self.GRAPH_KEYWORDS:
            if kw in q_lower:
                return "graph"
        return "vector"

    def classify_with_reason(self, question: str) -> dict:
        q_lower = question.lower()
        for kw in self.GRAPH_KEYWORDS:
            if kw in q_lower:
                return {"route": "graph", "reason": f"keyword match: '{kw}'", "question": question}
        return {"route": "vector", "reason": "no graph keywords found", "question": question}

# ─── TODO 2: Vector Query ─────────────────────────────────────────────────────
def vector_query(vectorstore, llm, question: str, k: int = 5) -> dict:
    docs = vectorstore.similarity_search(question, k=k)
    context = "\n\n".join([f"--- Function: {d.metadata.get('function')} (File: {d.metadata.get('file')}) ---\n{d.page_content}" for d in docs])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert coding assistant. Explain the code clearly based on context."),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    chain = prompt | llm
    res = chain.invoke({"context": context, "question": question})
    return {
        "answer": res.content,
        "source": "vector",
        "retrieved_docs": [d.metadata for d in docs]
    }

# ─── Helper & TODO 3: Graph Query ─────────────────────────────────────────────
def extract_function_name(question: str) -> Optional[str]:
    words = question.replace("?", "").replace("()", "").split()
    trigger = {"calls", "call", "called", "uses", "use", "imports", "import"}
    for i, w in enumerate(words):
        if w.lower() in trigger:
            if i > 0:
                candidate = words[i - 1].strip("'\".,")
                if candidate.lower() not in {"what", "who", "which", "does", "function", "the"}:
                    return candidate
            if i + 1 < len(words):
                candidate = words[i + 1].strip("'\".,")
                if candidate:
                    return candidate
    return None

def graph_query(conn, llm, question: str) -> dict:
    fn_name = extract_function_name(question)
    if fn_name:
        cypher = f"MATCH (a:Function)-[:CALLS]->(b:Function) WHERE b.name ENDS WITH '{fn_name}' OR a.name ENDS WITH '{fn_name}' RETURN a.name AS Caller, b.name AS Callee"
    else:
        cypher = "MATCH (a:Function)-[:CALLS]->(b:Function) RETURN a.name AS Caller, b.name AS Callee LIMIT 10"

    try:
        df = conn.execute(cypher).get_as_df()
        context = df.to_string() if not df.empty else "No graph relationship found."
    except Exception:
        context = "Error executing graph query."
        df = None

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a code architecture expert. Analyze function calls and relationships."),
        ("human", "Graph Call Relationship Data:\n{context}\n\nQuestion: {question}")
    ])
    chain = prompt | llm
    res = chain.invoke({"context": context, "question": question})
    return {
        "answer": res.content,
        "source": "graph",
        "graph_context": df.to_dict(orient="records") if df is not None else []
    }

# ─── TODO 4: HybridRAG Class ─────────────────────────────────────────────────
class HybridRAG:
    def __init__(self, vectorstore_path: str, graph_db_path: str):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
        db = kuzu.Database(graph_db_path)
        self.conn = kuzu.Connection(db)
        self.llm = ChatOllama(model="qwen2.5-coder:1.5b", temperature=0)
        self.router = QuestionRouter()

    def query(self, question: str, verbose: bool = False) -> dict:
        route_info = self.router.classify_with_reason(question)
        route = route_info["route"]
        if verbose:
            print(f"[HybridRAG Route] {route} | Reason: {route_info['reason']}")
        
        if route == "graph":
            res = self._graph_query(question)
        else:
            res = self._vector_query(question)
        
        res["reason"] = route_info["reason"]
        return res

    def _vector_query(self, question: str) -> dict:
        return vector_query(self.vectorstore, self.llm, question)

    def _graph_query(self, question: str) -> dict:
        return graph_query(self.conn, self.llm, question)

# ─── TODO 5: LLM Router ───────────────────────────────────────────────────────
class LLMQuestionRouter:
    def __init__(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Classify this question as 'vector' or 'graph'.\n'vector': HOW code works, algorithms, concepts\n'graph': RELATIONSHIPS — who calls what, what depends on what\nRespond with ONLY 'vector' or 'graph'."),
            ("human", "{question}")
        ])
        llm = ChatOllama(model="qwen2.5-coder:1.5b", temperature=0)
        self.chain = prompt | llm

    def classify(self, question: str) -> str:
        res = self.chain.invoke({"question": question})
        text = res.content.strip().lower()
        return "graph" if "graph" in text else "vector"