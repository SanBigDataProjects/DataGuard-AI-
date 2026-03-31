import pandas as pd
import os

def load_data(file_path):
    """
    Load data from CSV or Excel file
    Returns cleaned dataframe
    """
    try:
        # Get file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Read file based on extension
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        print(f"✅ Data loaded successfully!")
        print(f"📊 Shape: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"📋 Columns: {list(df.columns)}")
        
        return df
    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        return None


def get_basic_info(df):
    """
    Get basic information about the dataframe
    """
    info = {
        "total_rows": df.shape[0],
        "total_columns": df.shape[1],
        "column_names": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
    }
    return info


def clean_column_names(df):
    """
    Clean column names:
    - Strip whitespace
    - Convert to lowercase
    - Replace spaces with underscores
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )
    return df


def remove_empty_rows(df):
    """
    Remove rows where ALL values are empty
    """
    original_count = len(df)
    df = df.dropna(how='all')
    removed = original_count - len(df)
    
    if removed > 0:
        print(f"🧹 Removed {removed} completely empty rows")
    
    return df


def run_etl_pipeline(file_path):
    """
    Main ETL function — runs all steps in order:
    1. Load data
    2. Clean column names
    3. Remove empty rows
    4. Return clean dataframe + basic info
    """
    print("🚀 Starting ETL Pipeline...")
    print("-" * 40)
    
    # Step 1 — Load data
    df = load_data(file_path)
    
    if df is None:
        return None, None
    
    # Step 2 — Clean column names
    df = clean_column_names(df)
    print(f"✅ Column names cleaned")
    
    # Step 3 — Remove completely empty rows
    df = remove_empty_rows(df)
    
    # Step 4 — Get basic info
    info = get_basic_info(df)
    
    print("-" * 40)
    print("✅ ETL Pipeline Complete!")
    
    return df, info