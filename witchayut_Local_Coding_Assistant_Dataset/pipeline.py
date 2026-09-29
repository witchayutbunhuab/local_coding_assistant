"""Main execution pipeline for running analysis on datasets."""
from typing import List, Dict, Any
from data_processor import calculate_summary_stats, normalize_data

def run_pipeline(raw_dataset: List[float]) -> Dict[str, Any]:
    """Execute the full data analysis pipeline."""
    stats = calculate_summary_stats(raw_dataset)
    normalized = normalize_data(raw_dataset)
    return {
        "summary": stats,
        "normalized_data": normalized
    }

if __name__ == "__main__":
    sample_data = [10.0, 20.0, 30.0, 40.0, 50.0]
    results = run_pipeline(sample_data)
    print("Pipeline Results:", results)