
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
