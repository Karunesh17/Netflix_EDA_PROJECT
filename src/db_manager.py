"""
src/db_manager.py
SQLite Database Setup & Data Ingestion Manager
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import sqlite3
import pandas as pd

def get_db_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "data", "processed", "movies_analytics.db")

def init_database():
    """Create normalized SQLite database, schema, indexes and load processed data."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = get_db_path()
    movies_csv = os.path.join(base_dir, "data", "processed", "movies_cleaned.csv")
    genres_csv = os.path.join(base_dir, "data", "processed", "movie_genres.csv")
    
    if not os.path.exists(movies_csv) or not os.path.exists(genres_csv):
        from src.preprocessing import run_pipeline
        run_pipeline()
        
    df_movies = pd.read_csv(movies_csv)
    df_genres = pd.read_csv(genres_csv)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop existing tables if re-initializing
    cursor.execute("DROP TABLE IF EXISTS movie_genres;")
    cursor.execute("DROP TABLE IF EXISTS movies;")
    
    # 1. DDL for movies table
    cursor.execute("""
    CREATE TABLE movies (
        movie_id INTEGER PRIMARY KEY,
        Title TEXT NOT NULL,
        Release_Date TEXT NOT NULL,
        Release_Year INTEGER NOT NULL,
        Release_Month INTEGER NOT NULL,
        Release_Day INTEGER NOT NULL,
        Decade INTEGER NOT NULL,
        Decade_Label TEXT NOT NULL,
        Overview TEXT,
        Popularity REAL NOT NULL,
        Vote_Count INTEGER NOT NULL,
        Vote_Average REAL NOT NULL,
        Rating_Status TEXT NOT NULL,
        Vote_Average_Rated_Only REAL,
        Rating_Tier TEXT NOT NULL,
        Vote_Volume_Tier TEXT NOT NULL,
        Original_Language TEXT NOT NULL,
        Genre TEXT NOT NULL,
        Genre_Count INTEGER NOT NULL,
        Poster_Url TEXT
    );
    """)
    
    # 2. DDL for normalized movie_genres bridge table
    cursor.execute("""
    CREATE TABLE movie_genres (
        movie_id INTEGER NOT NULL,
        genre TEXT NOT NULL,
        PRIMARY KEY (movie_id, genre),
        FOREIGN KEY (movie_id) REFERENCES movies (movie_id) ON DELETE CASCADE
    );
    """)
    
    # Load data into SQLite
    df_movies.to_sql('movies', conn, if_exists='append', index=False)
    df_genres.to_sql('movie_genres', conn, if_exists='append', index=False)
    
    # Create performance indexes
    cursor.execute("CREATE INDEX idx_movies_year ON movies (Release_Year);")
    cursor.execute("CREATE INDEX idx_movies_lang ON movies (Original_Language);")
    cursor.execute("CREATE INDEX idx_movies_rating ON movies (Vote_Average);")
    cursor.execute("CREATE INDEX idx_movies_votes ON movies (Vote_Count);")
    cursor.execute("CREATE INDEX idx_genres_genre ON movie_genres (genre);")
    
    conn.commit()
    
    # Integrity verifications
    cursor.execute("SELECT COUNT(*) FROM movies;")
    m_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM movie_genres;")
    g_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"[+] Initialized SQLite Database at: {db_path}")
    print(f"    - Table 'movies': {m_count} rows loaded")
    print(f"    - Table 'movie_genres': {g_count} rows loaded")
    assert m_count == 9827, "DB load mismatch for movies!"
    assert g_count == 25793, "DB load mismatch for movie_genres!"
    return db_path

if __name__ == "__main__":
    init_database()
