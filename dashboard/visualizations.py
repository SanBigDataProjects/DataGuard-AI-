import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_health_score_gauge(score):
    """Create a gauge chart for health score"""
    
    # Color based on score
    if score >= 90:
        color = "green"
    elif score >= 70:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Data Health Score", 'font': {'size': 24}},
        delta={'reference': 100},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccc"},
                {'range': [50, 75], 'color': "#ffe0b2"},
                {'range': [75, 100], 'color': "#c8e6c9"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig


def create_missing_values_chart(missing_values):
    """Create bar chart for missing values"""
    
    if not missing_values:
        return None
    
    columns = [item['column'] for item in missing_values]
    percentages = [item['missing_percent'] for item in missing_values]
    counts = [item['missing_count'] for item in missing_values]
    
    fig = px.bar(
        x=columns,
        y=percentages,
        title="Missing Values by Column (%)",
        labels={'x': 'Column', 'y': 'Missing (%)'},
        color=percentages,
        color_continuous_scale='Reds',
        text=counts
    )
    
    fig.update_traces(texttemplate='%{text} missing', 
                      textposition='outside')
    fig.update_layout(height=350)
    return fig


def create_issues_summary_chart(results):
    """Create pie chart showing distribution of issues"""
    
    missing_count = sum(
        item['missing_count'] 
        for item in results['missing_values']
    )
    duplicate_count = results['duplicates']['duplicate_count']
    outlier_count = sum(
        item['outlier_count'] 
        for item in results['outliers']
    )
    invalid_count = sum(
        item['count'] 
        for item in results['invalid_values']
    )
    
    labels = ['Missing Values', 'Duplicates', 
              'Outliers', 'Invalid Values']
    values = [missing_count, duplicate_count, 
              outlier_count, invalid_count]
    
    # Only show non-zero values
    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    
    if not filtered:
        return None
        
    labels, values = zip(*filtered)
    
    fig = px.pie(
        values=values,
        names=labels,
        title="Distribution of Data Quality Issues",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    fig.update_layout(height=350)
    return fig


def create_data_overview_chart(df):
    """Create overview of data types"""
    
    dtype_counts = df.dtypes.astype(str).value_counts()
    
    fig = px.bar(
        x=dtype_counts.index,
        y=dtype_counts.values,
        title="Column Data Types",
        labels={'x': 'Data Type', 'y': 'Count'},
        color=dtype_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=300)
    return fig