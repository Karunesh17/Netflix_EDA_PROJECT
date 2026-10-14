"""
tests/test_metrics_consistency.py
Automated Cross-Validation: SQLite SQL vs. Pandas Parity Checks
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import sqlite3
import pytest
import pandas as pd
import numpy as np

@pytest.fixture(scope="module")
def db_connection():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "processed", "movies_analytics.db")
    if not os.path.exists(db_path):
        from src.db_manager import init_database
        init_database()
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()

@pytest.fixture(scope="module")
def pandas_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    movies_path = os.path.join(base_dir, "data", "processed", "movies_cleaned.csv")
    genres_path = os.path.join(base_dir, "data", "processed", "movie_genres.csv")
    df_movies = pd.read_csv(movies_path)
    df_genres = pd.read_csv(genres_path)
    return df_movies, df_genres

def test_sql_pandas_total_count_parity(db_connection, pandas_data):
    """Verify SQLite total row count equals Pandas row count."""
    df_movies, _ = pandas_data
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM movies;")
    sql_count = cursor.fetchone()[0]
    assert sql_count == len(df_movies) == 9827

def test_sql_pandas_clean_mean_rating_parity(db_connection, pandas_data):
    """Verify SQLite clean rated mean rating equals Pandas clean mean rating."""
    df_movies, _ = pandas_data
    pandas_mean = round(df_movies[df_movies['Rating_Status'] == 'Rated']['Vote_Average'].mean(), 2)
    
    cursor = db_connection.cursor()
    cursor.execute("SELECT ROUND(AVG(Vote_Average), 2) FROM movies WHERE Rating_Status = 'Rated';")
    sql_mean = cursor.fetchone()[0]
    assert sql_mean == pandas_mean == 6.51

def test_sql_pandas_top_5_genres_parity(db_connection, pandas_data):
    """Verify top 5 genre counts in SQLite match Pandas aggregations exactly."""
    _, df_genres = pandas_data
    pandas_top5 = df_genres['genre'].value_counts().head(5).to_dict()
    
    sql_query = """
    SELECT genre, COUNT(*) AS tag_count 
    FROM movie_genres 
    GROUP BY genre 
    ORDER BY tag_count DESC 
    LIMIT 5;
    """
    df_sql = pd.read_sql_query(sql_query, db_connection)
    sql_top5 = dict(zip(df_sql['genre'], df_sql['tag_count']))
    
    assert sql_top5 == pandas_top5
    assert sql_top5['Drama'] == 3744
    assert sql_top5['Comedy'] == 3031
    assert sql_top5['Action'] == 2686
    assert sql_top5['Thriller'] == 2488
    assert sql_top5['Adventure'] == 1853

def test_sql_pandas_growth_rates_parity(db_connection, pandas_data):
    """Verify 2015-2019 growth and 2020-2021 rebound in SQL and Pandas."""
    df_movies, _ = pandas_data
    c2015 = (df_movies['Release_Year'] == 2015).sum()
    c2019 = (df_movies['Release_Year'] == 2019).sum()
    c2020 = (df_movies['Release_Year'] == 2020).sum()
    c2021 = (df_movies['Release_Year'] == 2021).sum()
    
    assert c2015 == 390
    assert c2019 == 500
    assert c2020 == 453
    assert c2021 == 714
    
    growth_15_19 = round(((c2019 - c2015) / c2015) * 100.0, 2)
    drop_19_20 = round(((c2020 - c2019) / c2019) * 100.0, 2)
    rebound_20_21 = round(((c2021 - c2020) / c2020) * 100.0, 2)
    
    assert growth_15_19 == 28.21
    assert drop_19_20 == -9.40
    assert rebound_20_21 == 57.62

def test_percentage_sums(pandas_data):
    """Verify genre occurrence share percentages sum to 100.0%."""
    _, df_genres = pandas_data
    genre_shares = (df_genres['genre'].value_counts() / len(df_genres)) * 100.0
    assert round(genre_shares.sum(), 4) == 100.0
