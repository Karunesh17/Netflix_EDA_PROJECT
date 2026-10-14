"""
tests/test_dashboard_loading.py
Verify Dashboard Data Loaders & Query Execution Performance
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import pytest
import pandas as pd
from dashboard.utils import load_dashboard_data, execute_sql_query

def test_dashboard_data_loading():
    """Assert load_dashboard_data successfully retrieves all 3 primary dataframes."""
    df_movies, df_genres, df_merged = load_dashboard_data()
    assert isinstance(df_movies, pd.DataFrame)
    assert isinstance(df_genres, pd.DataFrame)
    assert isinstance(df_merged, pd.DataFrame)
    
    assert len(df_movies) == 9827
    assert len(df_genres) == 25793
    assert len(df_merged) == 25793

def test_dashboard_query_executor():
    """Assert execute_sql_query returns correct results from SQLite database."""
    query = "SELECT COUNT(*) AS total FROM movies WHERE Rating_Status = 'Unrated';"
    df_res = execute_sql_query(query)
    assert isinstance(df_res, pd.DataFrame)
    assert df_res.loc[0, 'total'] == 100
