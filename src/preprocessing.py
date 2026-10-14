"""
src/preprocessing.py
Reproducible Data Preprocessing & Analytics Engineering Pipeline
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import sys
import pandas as pd
import numpy as np

def get_data_paths():
    """Resolve project directory paths dynamically."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "mymoviedb.csv")
    if not os.path.exists(raw_path):
        raw_path = os.path.join(base_dir, "mymoviedb.csv")
    
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    movies_out = os.path.join(processed_dir, "movies_cleaned.csv")
    genres_out = os.path.join(processed_dir, "movie_genres.csv")
    
    return raw_path, movies_out, genres_out

def load_raw_dataset(raw_path):
    """Load raw dataset with proper encoding and line termination."""
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Source file not found at: {raw_path}")
    df = pd.read_csv(raw_path, lineterminator='\n')
    print(f"[+] Loaded raw dataset: {len(df)} rows, {len(df.columns)} columns")
    return df

def clean_and_transform_movies(df_raw):
    """
    Transform raw movie data into an analytics-ready dimensional table:
    - Adds surrogate primary key: movie_id (1..N)
    - Parses dates and extracts temporal attributes
    - Classifies rating status to handle 0-vote unrated titles properly
    - Creates audience score categories
    - Preserves all original columns without silent data loss
    """
    df = df_raw.copy()
    
    # 1. Assign surrogate primary key
    df.insert(0, 'movie_id', range(1, len(df) + 1))
    
    # 2. String sanitation
    text_cols = ['Title', 'Overview', 'Original_Language', 'Genre', 'Poster_Url']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # 3. Temporal transformations
    df['Release_Date'] = pd.to_datetime(df['Release_Date'], errors='coerce')
    if df['Release_Date'].isnull().sum() > 0:
        raise ValueError(f"Found {df['Release_Date'].isnull().sum()} unparseable dates!")
        
    df['Release_Year'] = df['Release_Date'].dt.year.astype(int)
    df['Release_Month'] = df['Release_Date'].dt.month.astype(int)
    df['Release_Day'] = df['Release_Date'].dt.day.astype(int)
    df['Decade'] = (df['Release_Year'] // 10) * 10
    df['Decade_Label'] = df['Decade'].astype(str) + "s"
    
    # 4. Numerical validation
    df['Popularity'] = pd.to_numeric(df['Popularity'], errors='raise')
    df['Vote_Count'] = pd.to_numeric(df['Vote_Count'], errors='raise').astype(int)
    df['Vote_Average'] = pd.to_numeric(df['Vote_Average'], errors='raise')
    
    assert (df['Popularity'] >= 0).all(), "Negative popularity values found!"
    assert (df['Vote_Count'] >= 0).all(), "Negative vote count values found!"
    assert ((df['Vote_Average'] >= 0.0) & (df['Vote_Average'] <= 10.0)).all(), "Vote_Average out of [0, 10] range!"
    
    # 5. Rating Status & Quality Engineering (handling zero-vote anomaly)
    # 100 films have Vote_Count == 0 and Vote_Average == 0.0 (unrated / unreleased)
    df['Rating_Status'] = np.where(df['Vote_Count'] == 0, 'Unrated', 'Rated')
    
    # Score for statistical rating analysis (excludes unrated 0.0 from dragging down means)
    df['Vote_Average_Rated_Only'] = np.where(df['Vote_Count'] == 0, np.nan, df['Vote_Average'])
    
    # Rating Tier classification
    def assign_rating_tier(row):
        if row['Rating_Status'] == 'Unrated':
            return 'Unrated (0 Votes)'
        score = row['Vote_Average']
        if score < 5.0:
            return 'Poor (< 5.0)'
        elif score < 6.5:
            return 'Below Average (5.0 - 6.4)'
        elif score < 7.5:
            return 'Good (6.5 - 7.4)'
        else:
            return 'Acclaimed (>= 7.5)'
            
    df['Rating_Tier'] = df.apply(assign_rating_tier, axis=1)
    
    # 6. Vote Volume Confidence Tier
    def assign_vote_tier(count):
        if count == 0:
            return 'No Votes (0)'
        elif count < 100:
            return 'Low Volume (1 - 99)'
        elif count < 1000:
            return 'Moderate Volume (100 - 999)'
        else:
            return 'High Volume (1000+)'
            
    df['Vote_Volume_Tier'] = df['Vote_Count'].apply(assign_vote_tier)
    
    # 7. Multi-genre count per film
    df['Genre_Count'] = df['Genre'].apply(lambda x: len([g.strip() for g in x.split(',') if g.strip()]))
    
    return df

def create_genre_bridge_table(df_cleaned):
    """
    Create a normalized bridge table (movie_id <-> genre) for relational SQL & multi-label analytics.
    Each row represents a single genre tag attached to a movie.
    """
    records = []
    for _, row in df_cleaned.iterrows():
        m_id = row['movie_id']
        raw_genres = str(row['Genre']).split(',')
        for g in raw_genres:
            g_clean = g.strip()
            if g_clean:
                records.append({
                    'movie_id': m_id,
                    'genre': g_clean
                })
                
    df_genres = pd.DataFrame(records)
    return df_genres

def validate_pipeline_artifacts(df_movies, df_genres):
    """Execute automated assertions to ensure zero data regression."""
    print("\n[+] Running Preprocessing Validation Assertions...")
    
    # 1. Row counts
    assert len(df_movies) == 9827, f"Movie count mismatch: {len(df_movies)} != 9827"
    assert len(df_genres) == 25793, f"Genre occurrences mismatch: {len(df_genres)} != 25793"
    
    # 2. Key uniqueness
    assert df_movies['movie_id'].nunique() == 9827, "movie_id is not unique!"
    
    # 3. Unrated preservation
    unrated_count = (df_movies['Rating_Status'] == 'Unrated').sum()
    assert unrated_count == 100, f"Unrated count mismatch: {unrated_count} != 100"
    
    # 4. Genre integrity
    assert df_genres['genre'].nunique() == 19, f"Unique genre count mismatch: {df_genres['genre'].nunique()} != 19"
    
    # 5. Referential integrity
    orphan_genres = set(df_genres['movie_id']) - set(df_movies['movie_id'])
    assert len(orphan_genres) == 0, f"Found {len(orphan_genres)} orphaned genre rows!"
    
    # 6. Null checks on critical columns
    critical_cols = ['movie_id', 'Title', 'Release_Date', 'Release_Year', 'Popularity', 'Vote_Count']
    for col in critical_cols:
        assert df_movies[col].isnull().sum() == 0, f"Unexpected nulls in {col}!"
        
    print("    [PASSED] All 6 automated data quality assertions satisfied.")

def run_pipeline():
    """Main execution entry point."""
    print("=" * 60)
    print("STARTING DATA PREPROCESSING & ETL PIPELINE")
    print("=" * 60)
    
    raw_path, movies_out, genres_out = get_data_paths()
    df_raw = load_raw_dataset(raw_path)
    
    # Process
    df_movies = clean_and_transform_movies(df_raw)
    df_genres = create_genre_bridge_table(df_movies)
    
    # Validate
    validate_pipeline_artifacts(df_movies, df_genres)
    
    # Export
    df_movies.to_csv(movies_out, index=False)
    df_genres.to_csv(genres_out, index=False)
    print(f"\n[+] Exported cleaned movies table: {movies_out} ({len(df_movies)} rows)")
    print(f"[+] Exported normalized genres bridge table: {genres_out} ({len(df_genres)} rows)")
    print("=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    return df_movies, df_genres

if __name__ == "__main__":
    run_pipeline()
