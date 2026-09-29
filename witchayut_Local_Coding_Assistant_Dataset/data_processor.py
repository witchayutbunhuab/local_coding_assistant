"""Data processing module that utilizes math utilities."""
from typing import List, Dict, Any
from math_utils import mean, median, variance

def clean_data(raw_data: List[float]) -> List[float]:
    """Remove None or invalid numeric values from raw data."""
    return [x for x in raw_data if x is not None and isinstance(x, (int, float))]

def calculate_summary_stats(data: List[float]) -> Dict[str, float]:
    """Compute mean, median, and variance for a given dataset."""
    cleaned = clean_data(data)
    if not cleaned:
        return {"mean": 0.0, "median": 0.0, "variance": 0.0}
    
    avg_val = mean(cleaned)
    med_val = median(cleaned)
    var_val = variance(cleaned)
    
    return {
        "mean": avg_val,
        "median": med_val,
        "variance": var_val
    }

def normalize_data(data: List[float]) -> List[float]:
    """Normalize data using calculated mean."""
    cleaned = clean_data(data)
    avg = mean(cleaned)
    return [x - avg for x in cleaned]"""Data processing module that utilizes math utilities."""
from typing import List, Dict, Any
from math_utils import mean, median, variance

def clean_data(raw_data: List[float]) -> List[float]:
    """Remove None or invalid numeric values from raw data."""
    return [x for x in raw_data if x is not None and isinstance(x, (int, float))]

def calculate_summary_stats(data: List[float]) -> Dict[str, float]:
    """Compute mean, median, and variance for a given dataset."""
    cleaned = clean_data(data)
    if not cleaned:
        return {"mean": 0.0, "median": 0.0, "variance": 0.0}
    
    avg_val = mean(cleaned)
    med_val = median(cleaned)
    var_val = variance(cleaned)
    
    return {
        "mean": avg_val,
        "median": med_val,
        "variance": var_val
    }

def normalize_data(data: List[float]) -> List[float]:
    """Normalize data using calculated mean."""
    cleaned = clean_data(data)
    avg = mean(cleaned)
    return [x - avg for x in cleaned]