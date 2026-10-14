-- ==============================================================================
-- SQL Analytics File 1: Database Schema & Index Definitions
-- Database: movies_analytics.db (SQLite)
-- Purpose: Normalized relational tables for TMDb Movie Analytics
-- ==============================================================================

-- 1. Movies Primary Table
CREATE TABLE IF NOT EXISTS movies (
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

-- 2. Normalized Genre Bridge Table (1-to-Many / Multi-Label Normalization)
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER NOT NULL,
    genre TEXT NOT NULL,
    PRIMARY KEY (movie_id, genre),
    FOREIGN KEY (movie_id) REFERENCES movies (movie_id) ON DELETE CASCADE
);

-- 3. High-Performance Analytical Indexes
CREATE INDEX IF NOT EXISTS idx_movies_year ON movies (Release_Year);
CREATE INDEX IF NOT EXISTS idx_movies_lang ON movies (Original_Language);
CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies (Vote_Average);
CREATE INDEX IF NOT EXISTS idx_movies_votes ON movies (Vote_Count);
CREATE INDEX IF NOT EXISTS idx_genres_genre ON movie_genres (genre);
