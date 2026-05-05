import pandas as pd
import os

def write_to_parquet(data, filename):
    df = pd.DataFrame(data)
    # Ensure directory exists
    os.makedirs("data/raw", exist_ok=True)
    path = f"data/raw/{filename}.parquet"
    
    # Idempotency: Overwrite existing file for that specific ingestion window
    # In a real GCP/BigQuery scenario, we would partition by date
    df.to_parquet(path, index=False, engine='pyarrow')
    return path