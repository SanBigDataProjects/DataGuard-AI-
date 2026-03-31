import pandas as pd
import numpy as np

def run_all_checks(df):
    """Run all quality checks on the dataframe"""
    results = {
        "missing_values": check_missing_values(df),
        "duplicates": check_duplicates(df),
        "outliers": check_outliers(df),
        "invalid_values": check_invalid_values(df),
        "health_score": calculate_health_score(df)
    }
    return results

def check_missing_values(df):
    """Check for missing values in each column"""
    missing = df.isnull().sum()
    missing_percent = (missing / len(df)) * 100
    
    results = []
    for column in df.columns:
        if missing[column] > 0:
            results.append({
                "column": column,
                "missing_count": int(missing[column]),
                "missing_percent": round(float(missing_percent[column]), 2)
            })
    return results

def check_duplicates(df):
    """Check for duplicate rows excluding ID column"""
    
    # Columns to check for duplicates (exclude ID)
    cols_to_check = [col for col in df.columns 
                     if 'id' not in col.lower()]
    
    # Find duplicates
    full_duplicates = df.duplicated(
        subset=cols_to_check, 
        keep=False
    )
    duplicate_count = full_duplicates.sum() // 2
    duplicate_rows = df[full_duplicates].index.tolist()
    
    return {
        "duplicate_count": int(duplicate_count),
        "duplicate_rows": duplicate_rows,
        "columns_checked": cols_to_check
    }
def check_outliers(df):
    """Check for outliers in numeric columns"""
    results = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for column in numeric_cols:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[
            (df[column] < lower_bound) | 
            (df[column] > upper_bound)
        ]
        
        if len(outliers) > 0:
            results.append({
                "column": column,
                "outlier_count": len(outliers),
                "outlier_rows": outliers.index.tolist(),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2)
            })
    return results

def check_invalid_values(df):
    """Check for invalid values like negative salaries"""
    results = []
    
    # Check negative values in salary column if exists
    if 'salary' in df.columns:
        negative_salary = df[df['salary'] < 0]
        if len(negative_salary) > 0:
            results.append({
                "column": "salary",
                "issue": "Negative salary values",
                "affected_rows": negative_salary.index.tolist(),
                "count": len(negative_salary)
            })
    
    # Check age is reasonable if exists
    if 'age' in df.columns:
        invalid_age = df[(df['age'] < 18) | (df['age'] > 100)]
        if len(invalid_age) > 0:
            results.append({
                "column": "age",
                "issue": "Invalid age values",
                "affected_rows": invalid_age.index.tolist(),
                "count": len(invalid_age)
            })
    
    return results

def calculate_health_score(df):
    """Calculate overall data health score out of 100"""
    total_cells = df.shape[0] * df.shape[1]
    penalties = 0
    
    # Missing values penalty — 40 points max
    missing_cells = df.isnull().sum().sum()
    penalties += (missing_cells / total_cells) * 40
    
    # Duplicate penalty — 20 points max
    cols_to_check = [col for col in df.columns 
                     if 'id' not in col.lower()]
    duplicate_rows = df.duplicated(subset=cols_to_check).sum()
    penalties += (duplicate_rows / len(df)) * 20
    
    # Invalid values penalty — 20 points max
    if 'salary' in df.columns:
        negative_salary = len(df[df['salary'] < 0])
        penalties += (negative_salary / len(df)) * 10
    if 'age' in df.columns:
        invalid_age = len(df[
            (df['age'] < 18) | (df['age'] > 100)
        ])
        penalties += (invalid_age / len(df)) * 10
    
    # Outlier penalty — 20 points max
    numeric_cols = df.select_dtypes(
        include=['number']
    ).columns
    outlier_count = 0
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df[col] < Q1 - 1.5*IQR) | 
            (df[col] > Q3 + 1.5*IQR)
        ]
        outlier_count += len(outliers)
    penalties += (outlier_count / total_cells) * 20
    
    score = 100 - penalties
    score = max(0, min(100, score))
    return round(score, 1)