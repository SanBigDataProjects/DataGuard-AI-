import os
from dotenv import load_dotenv
from groq import Groq

# Load .env file
load_dotenv()

# Get API key explicitly
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key found: {api_key is not None}")

# Initialize Groq client
#client = Groq(api_key=api_key)
client = Groq(api_key="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")

def explain_quality_issues(results, df_info):
    issues_summary = build_issues_summary(results)
    
    prompt = f"""
You are a friendly data quality expert helping a business understand their data problems.

Dataset Information:
- Total Rows: {df_info['total_rows']}
- Total Columns: {df_info['total_columns']}
- Columns: {', '.join(df_info['column_names'])}

Data Quality Issues Found:
{issues_summary}

Health Score: {results['health_score']}/100

Please provide:
1. A simple friendly summary of what problems were found
2. Why each problem matters for the business
3. Specific recommendations to fix each issue
4. Overall assessment of data health

Keep your response clear and simple.
Use bullet points and emojis to make it easy to read.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    return response.choices[0].message.content


def build_issues_summary(results):
    summary = []
    
    if results['missing_values']:
        summary.append("MISSING VALUES:")
        for item in results['missing_values']:
            summary.append(
                f"  - Column '{item['column']}': "
                f"{item['missing_count']} missing values "
                f"({item['missing_percent']}%)"
            )
    
    if results['duplicates']['duplicate_count'] > 0:
        summary.append(f"\nDUPLICATE ROWS:")
        summary.append(
            f"  - Found {results['duplicates']['duplicate_count']} "
            f"duplicate records at rows: "
            f"{results['duplicates']['duplicate_rows']}"
        )
    
    if results['outliers']:
        summary.append("\nOUTLIERS:")
        for item in results['outliers']:
            summary.append(
                f"  - Column '{item['column']}': "
                f"{item['outlier_count']} outlier(s) found "
                f"(expected range: {item['lower_bound']} "
                f"to {item['upper_bound']})"
            )
    
    if results['invalid_values']:
        summary.append("\nINVALID VALUES:")
        for item in results['invalid_values']:
            summary.append(
                f"  - Column '{item['column']}': "
                f"{item['issue']} "
                f"({item['count']} record(s) affected)"
            )
    
    return '\n'.join(summary)


def get_fix_suggestions(results):
    prompt = f"""
You are a data engineer helping fix data quality issues.

Issues found:
{build_issues_summary(results)}

For each issue provide:
1. The exact problem
2. One specific fix recommendation
3. Python code snippet to fix it

Keep it short and practical.
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    
    return response.choices[0].message.content
