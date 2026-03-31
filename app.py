import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from etl.pipeline import run_etl_pipeline, get_basic_info
from checks.quality_checks import run_all_checks
from ai.explainer import explain_quality_issues, get_fix_suggestions
from dashboard.visualizations import (
    create_health_score_gauge,
    create_missing_values_chart,
    create_issues_summary_chart,
    create_data_overview_chart
)

# Page configuration
st.set_page_config(
    page_title="DataGuard AI",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .issue-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown(
        '<p class="main-header">🛡️ DataGuard AI</p>', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">AI-Powered Data Quality Monitor</p>', 
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/shield.png", 
                 width=80)
        st.title("DataGuard AI")
        st.markdown("*Your intelligent data quality assistant*")
        st.divider()
        
        st.subheader("📁 Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your data file to analyze"
        )
        
        st.divider()
        st.markdown("### How it works")
        st.markdown("1. 📤 Upload your data file")
        st.markdown("2. 🔍 DataGuard scans for issues")
        st.markdown("3. 🤖 AI explains what's wrong")
        st.markdown("4. ✅ Get fix recommendations")
        
        st.divider()
        st.markdown("Built with ❤️ by Sanyukta Singh")
        st.markdown("*OpenAI Codex Creator Challenge*")
    
    # Main content
    if uploaded_file is None:
        # Welcome screen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h2>🔍</h2>
                <h3>Smart Detection</h3>
                <p>Automatically finds missing values, 
                duplicates, outliers, and invalid data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h2>🤖</h2>
                <h3>AI Explanations</h3>
                <p>Groq LLaMA AI explains every issue 
                in plain English your team can understand</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h2>📊</h2>
                <h3>Health Score</h3>
                <p>Get an instant data health score 
                out of 100 with visual dashboard</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.info("👈 Upload your data file in the sidebar to get started!")
        
        # Demo option
        if st.button("🎯 Try with Sample Data", 
                     type="primary",
                     use_container_width=True):
            analyze_data("data/sample_data.csv")
    
    else:
        # Save uploaded file temporarily
        temp_path = f"data/temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        analyze_data(temp_path)


def analyze_data(file_path):
    """Main analysis function"""
    
    with st.spinner("🔍 Analyzing your data..."):
        # Run ETL Pipeline
        df, info = run_etl_pipeline(file_path)
        
        if df is None:
            st.error("❌ Could not load file. Please check the format.")
            return
        
        # Run Quality Checks
        results = run_all_checks(df)
    
    st.success("✅ Analysis Complete!")
    
    # Top metrics row
    st.subheader("📊 Data Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Rows", info['total_rows'])
    with col2:
        st.metric("Total Columns", info['total_columns'])
    with col3:
        missing = sum(
            i['missing_count'] 
            for i in results['missing_values']
        )
        st.metric("Missing Values", missing, 
                  delta=f"-{missing}" if missing > 0 else None)
    with col4:
        dupes = results['duplicates']['duplicate_count']
        st.metric("Duplicates", dupes,
                  delta=f"-{dupes}" if dupes > 0 else None)
    with col5:
        st.metric("Health Score", 
                  f"{results['health_score']}/100")
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Health Score Gauge
        gauge = create_health_score_gauge(results['health_score'])
        st.plotly_chart(gauge, use_container_width=True)
    
    with col2:
        # Issues Summary Pie
        pie = create_issues_summary_chart(results)
        if pie:
            st.plotly_chart(pie, use_container_width=True)
        else:
            st.markdown("""
            <div class="success-box">
                <h3>🎉 No Issues Found!</h3>
                <p>Your data looks clean!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Missing Values Chart
    if results['missing_values']:
        missing_chart = create_missing_values_chart(
            results['missing_values']
        )
        if missing_chart:
            st.plotly_chart(missing_chart, use_container_width=True)
    
    st.divider()
    
    # Detailed Issues
    st.subheader("🔍 Detailed Issues Found")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "❌ Missing Values", 
        "👥 Duplicates", 
        "📈 Outliers",
        "⚠️ Invalid Values"
    ])
    
    with tab1:
        if results['missing_values']:
            for item in results['missing_values']:
                st.markdown(f"""
                <div class="issue-box">
                    <b>Column: {item['column']}</b><br>
                    Missing: {item['missing_count']} values 
                    ({item['missing_percent']}%)
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No missing values found!")
    
    with tab2:
        if results['duplicates']['duplicate_count'] > 0:
            st.markdown(f"""
            <div class="issue-box">
                <b>Found {results['duplicates']['duplicate_count']} 
                duplicate records</b><br>
                Affected rows: {results['duplicates']['duplicate_rows']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ No duplicates found!")
    
    with tab3:
        if results['outliers']:
            for item in results['outliers']:
                st.markdown(f"""
                <div class="issue-box">
                    <b>Column: {item['column']}</b><br>
                    {item['outlier_count']} outlier(s) found<br>
                    Expected range: {item['lower_bound']} 
                    to {item['upper_bound']}<br>
                    Affected rows: {item['outlier_rows']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No outliers found!")
    
    with tab4:
        if results['invalid_values']:
            for item in results['invalid_values']:
                st.markdown(f"""
                <div class="issue-box">
                    <b>Column: {item['column']}</b><br>
                    Issue: {item['issue']}<br>
                    Affected rows: {item['affected_rows']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No invalid values found!")
    
    st.divider()
    
    # Raw Data Preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.divider()
    
    # AI Explanation Section
    st.subheader("🤖 AI Analysis & Recommendations")
    
    if st.button("🚀 Get AI Explanation", 
                 type="primary",
                 use_container_width=True):
        with st.spinner("🤖 AI is analyzing your data..."):
            explanation = explain_quality_issues(results, info)
        
        st.markdown(explanation)
        
        st.divider()
        
        with st.spinner("💡 Getting fix suggestions..."):
            suggestions = get_fix_suggestions(results)
        
        st.subheader("💡 How to Fix These Issues")
        st.markdown(suggestions)


if __name__ == "__main__":
    main()