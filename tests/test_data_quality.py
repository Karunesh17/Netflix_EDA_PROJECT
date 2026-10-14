"""
tests/test_data_quality.py
Automated Data Quality & Pipeline Integrity Test Suite
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import pytest
import pandas as pd
import numpy as np

@pytest.fixture(scope="module")
def project_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "mymoviedb.csv")
    cleaned_path = os.path.join(base_dir, "data", "processed", "movies_cleaned.csv")
    genres_path = os.path.join(base_dir, "data", "processed", "movie_genres.csv")
    
    df_raw = pd.read_csv(raw_path, lineterminator='\n')
    df_cleaned = pd.read_csv(cleaned_path)
    df_genres = pd.read_csv(genres_path)
    return df_raw, df_cleaned, df_genres

def test_row_counts(project_data):
    """Assert raw and cleaned movie datasets have exactly 9,827 rows."""
    df_raw, df_cleaned, df_genres = project_data
    assert len(df_raw) == 9827, f"Raw row count mismatch: {len(df_raw)}"
    assert len(df_cleaned) == 9827, f"Cleaned row count mismatch: {len(df_cleaned)}"
    assert len(df_genres) == 25793, f"Genre occurrence count mismatch: {len(df_genres)}"

def test_unique_movie_ids(project_data):
    """Assert surrogate primary key movie_id is 100% unique."""
    _, df_cleaned, _ = project_data
    assert df_cleaned['movie_id'].nunique() == 9827
    assert df_cleaned['movie_id'].min() == 1
    assert df_cleaned['movie_id'].max() == 9827

def test_no_unexpected_nulls(project_data):
    """Assert zero missing values in critical analytical columns."""
    _, df_cleaned, df_genres = project_data
    critical_cols = ['movie_id', 'Title', 'Release_Date', 'Release_Year', 'Popularity', 'Vote_Count', 'Vote_Average', 'Rating_Status', 'Original_Language']
    for col in critical_cols:
        assert df_cleaned[col].isnull().sum() == 0, f"Found nulls in column {col}"
    assert df_genres['movie_id'].isnull().sum() == 0
    assert df_genres['genre'].isnull().sum() == 0

def test_unrated_zero_vote_preservation(project_data):
    """Assert exactly 100 unrated zero-vote films are preserved without data loss."""
    _, df_cleaned, _ = project_data
    unrated = df_cleaned[df_cleaned['Rating_Status'] == 'Unrated']
    assert len(unrated) == 100, f"Expected 100 unrated films, got {len(unrated)}"
    assert (unrated['Vote_Count'] == 0).all(), "Unrated films have non-zero vote counts!"
    assert (unrated['Vote_Average'] == 0.0).all(), "Unrated films have non-zero vote averages!"
    assert unrated['Vote_Average_Rated_Only'].isnull().all(), "Vote_Average_Rated_Only should be NaN for unrated!"

def test_genre_normalization_integrity(project_data):
    """Assert genres are normalized into 19 unique categories without orphaned keys."""
    _, df_cleaned, df_genres = project_data
    assert df_genres['genre'].nunique() == 19
    orphan_ids = set(df_genres['movie_id']) - set(df_cleaned['movie_id'])
    assert len(orphan_ids) == 0, f"Found orphaned genre movie_ids: {len(orphan_ids)}"

def test_date_parsing_range(project_data):
    """Assert valid date parsing and expected temporal coverage (1902 to 2024)."""
    _, df_cleaned, _ = project_data
    assert df_cleaned['Release_Year'].min() == 1902
    assert df_cleaned['Release_Year'].max() == 2024
    assert df_cleaned['Release_Month'].between(1, 12).all()
    assert df_cleaned['Release_Day'].between(1, 31).all()

def test_duplicate_handling_logic(project_data):
    """Assert 0 exact duplicate rows and 0 duplicate (Title, Release_Date) collisions."""
    df_raw, df_cleaned, _ = project_data
    assert df_raw.duplicated().sum() == 0
    assert df_cleaned.duplicated(subset=['Title', 'Release_Date']).sum() == 0
    assert df_cleaned.duplicated(subset=['Title']).sum() == 314
