-- TMDb Movie Data Analysis - SQL Queries
-- Database: SQLite (data/movies_analytics.db)
-- These queries answer specific questions about movie releases, genres, languages, and ratings.

-- -----------------------------------------------------------------------------
-- Query 1: Total movies, unique titles, and average rating
-- Check overall catalog size and calculate the average rating only for movies
-- that have at least one vote (excluding unrated movies where Vote_Count = 0).
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_movies,
    COUNT(DISTINCT Title) AS unique_titles,
    SUM(CASE WHEN Rating_Status = 'Unrated' THEN 1 ELSE 0 END) AS unrated_movies,
    ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS avg_rating_rated_only,
    ROUND(AVG(Popularity), 2) AS avg_popularity,
    MIN(Release_Year) AS earliest_year,
    MAX(Release_Year) AS latest_year
FROM movies;


-- -----------------------------------------------------------------------------
-- Query 2: Top 10 most common genres
-- Join the movies table with the normalized movie_genres bridge table to count
-- how many movies belong to each genre and calculate their percentage share.
-- -----------------------------------------------------------------------------
SELECT 
    mg.genre,
    COUNT(DISTINCT m.movie_id) AS movie_count,
    ROUND((COUNT(DISTINCT m.movie_id) * 100.0) / (SELECT COUNT(*) FROM movies), 2) AS percentage_of_catalog,
    ROUND(AVG(CASE WHEN m.Rating_Status = 'Rated' THEN m.Vote_Average ELSE NULL END), 2) AS avg_rating
FROM movie_genres mg
JOIN movies m ON mg.movie_id = m.movie_id
GROUP BY mg.genre
ORDER BY movie_count DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Query 3: Movies by language (English vs. international)
-- Group movies into English, top non-English languages, and other languages
-- to see the language breakdown.
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN Original_Language = 'en' THEN 'English'
        WHEN Original_Language = 'ja' THEN 'Japanese'
        WHEN Original_Language = 'es' THEN 'Spanish'
        WHEN Original_Language = 'fr' THEN 'French'
        WHEN Original_Language = 'ko' THEN 'Korean'
        ELSE 'Other Languages'
    END AS language_group,
    COUNT(*) AS movie_count,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM movies), 2) AS percentage_share
FROM movies
GROUP BY language_group
ORDER BY movie_count DESC;


-- -----------------------------------------------------------------------------
-- Query 4: Movie releases per year (2010 to 2022)
-- Look at how movie releases, average ratings, and popularity trended over the
-- last decade.
-- -----------------------------------------------------------------------------
SELECT 
    Release_Year,
    COUNT(*) AS movies_released,
    ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS avg_rating,
    ROUND(AVG(Popularity), 1) AS avg_popularity
FROM movies
WHERE Release_Year BETWEEN 2010 AND 2022
GROUP BY Release_Year
ORDER BY Release_Year ASC;


-- -----------------------------------------------------------------------------
-- Query 5: Year-over-year release growth (using LAG window function)
-- Use a CTE and LAG() to calculate the annual change and percentage growth 
-- in releases from 2015 to 2021 (showing the 2020 drop and 2021 rebound).
-- -----------------------------------------------------------------------------
WITH annual_releases AS (
    SELECT 
        Release_Year,
        COUNT(*) AS total_releases
    FROM movies
    WHERE Release_Year BETWEEN 2014 AND 2022
    GROUP BY Release_Year
),
growth_calc AS (
    SELECT 
        Release_Year,
        total_releases,
        LAG(total_releases, 1) OVER (ORDER BY Release_Year) AS previous_year_releases,
        total_releases - LAG(total_releases, 1) OVER (ORDER BY Release_Year) AS net_difference,
        ROUND(
            ((total_releases - LAG(total_releases, 1) OVER (ORDER BY Release_Year)) * 100.0) 
            / LAG(total_releases, 1) OVER (ORDER BY Release_Year), 
            2
        ) AS yoy_growth_percent
    FROM annual_releases
)
SELECT 
    Release_Year,
    total_releases,
    COALESCE(previous_year_releases, 0) AS previous_year_releases,
    COALESCE(net_difference, 0) AS net_difference,
    COALESCE(yoy_growth_percent, 0.0) AS yoy_growth_percent
FROM growth_calc
WHERE Release_Year >= 2015
ORDER BY Release_Year ASC;


-- -----------------------------------------------------------------------------
-- Query 6: Top 5 highest rated movies with at least 1,000 votes
-- Filter for movies with a minimum number of votes so that movies with only 1 or 2
-- 10/10 ratings do not distort the top rankings.
-- -----------------------------------------------------------------------------
SELECT 
    Title,
    Release_Year,
    Original_Language,
    Vote_Average,
    Vote_Count,
    Popularity
FROM movies
WHERE Vote_Count >= 1000
ORDER BY Vote_Average DESC, Vote_Count DESC
LIMIT 5;


-- -----------------------------------------------------------------------------
-- Query 7: Most common genre pairings (self-join on movie_genres)
-- Find which two genres appear together most often on the same movie.
-- Using g1.genre < g2.genre prevents duplicate combinations like (Action, Drama)
-- and (Drama, Action).
-- -----------------------------------------------------------------------------
SELECT 
    g1.genre AS first_genre,
    g2.genre AS second_genre,
    COUNT(*) AS times_paired_together
FROM movie_genres g1
JOIN movie_genres g2 
  ON g1.movie_id = g2.movie_id 
 AND g1.genre < g2.genre
GROUP BY g1.genre, g2.genre
ORDER BY times_paired_together DESC
LIMIT 5;
