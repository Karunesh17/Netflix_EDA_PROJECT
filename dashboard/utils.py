"""
dashboard/utils.py
Cached Data Loaders & Query Helpers for Streamlit Dashboard
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

def get_base_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@st.cache_data
def load_dashboard_data():
    """Load cleaned movies and genre bridge tables with caching."""
    base_dir = get_base_dir()
    movies_path = os.path.join(base_dir, "data", "processed", "movies_cleaned.csv")
    genres_path = os.path.join(base_dir, "data", "processed", "movie_genres.csv")
    
    # If not present, run preprocessing
    if not os.path.exists(movies_path) or not os.path.exists(genres_path):
        from src.preprocessing import run_pipeline
        run_pipeline()
        
    df_movies = pd.read_csv(movies_path)
    df_genres = pd.read_csv(genres_path)
    
    # Merge for multi-genre filtering
    df_merged = df_genres.merge(df_movies, on='movie_id')
    return df_movies, df_genres, df_merged

@st.cache_data
def execute_sql_query(query_str):
    """Execute arbitrary SQL query on the SQLite analytics database."""
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "data", "processed", "movies_analytics.db")
    if not os.path.exists(db_path):
        from src.db_manager import init_database
        init_database()
        
    conn = sqlite3.connect(db_path)
    df_res = pd.read_sql_query(query_str, conn)
    conn.close()
    return df_res
