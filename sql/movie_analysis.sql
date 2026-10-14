-- ==============================================================================
-- TMDb Movie Data Analysis — SQL Analytical Queries
-- Database Engine: SQLite (data/movies_analytics.db)
-- Author: Data Analyst Portfolio
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Catalog Volume & Clean Average Rating
-- Analytical Question: What is the total film volume, and what is the clean 
-- average rating when excluding unrated films (Vote_Count == 0)?
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_movies,
    COUNT(DISTINCT Title) AS unique_titles,
    SUM(CASE WHEN Rating_Status = 'Unrated' THEN 1 ELSE 0 END) AS unrated_movies,
    ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS clean_avg_rating,
    ROUND(AVG(Popularity), 2) AS avg_popularity,
    MIN(Release_Year) AS earliest_year,
    MAX(Release_Year) AS latest_year
FROM movies;


-- ------------------------------------------------------------------------------
-- QUERY 2: Top 10 Genres by Film Title Volume
-- Analytical Question: Which 10 movie genres have the highest title penetration
-- across the catalog?
-- Demonstrates: Relational JOIN on normalized bridge table, GROUP BY, ORDER BY.
-- ------------------------------------------------------------------------------
SELECT 
    mg.genre,
    COUNT(DISTINCT m.movie_id) AS movie_count,
    ROUND((COUNT(DISTINCT m.movie_id) * 100.0) / (SELECT COUNT(*) FROM movies), 2) AS title_penetration_pct,
    ROUND(AVG(CASE WHEN m.Rating_Status = 'Rated' THEN m.Vote_Average ELSE NULL END), 2) AS avg_rating
FROM movie_genres mg
JOIN movies m ON mg.movie_id = m.movie_id
GROUP BY mg.genre
ORDER BY movie_count DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 3: Linguistic Breakdown & Market Concentration
-- Analytical Question: How is the catalog divided between English and major
-- international languages?
-- Demonstrates: Conditional CASE WHEN grouping and percentage calculations.
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN Original_Language = 'en' THEN 'English'
        WHEN Original_Language = 'ja' THEN 'Japanese'
        WHEN Original_Language = 'es' THEN 'Spanish'
        WHEN Original_Language = 'fr' THEN 'French'
        WHEN Original_Language = 'ko' THEN 'Korean'
        ELSE 'Other International'
    END AS language_group,
    COUNT(*) AS title_count,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM movies), 2) AS catalog_share_pct
FROM movies
GROUP BY language_group
ORDER BY title_count DESC;


-- ------------------------------------------------------------------------------
-- QUERY 4: Annual Release Velocity & Production Trends (2010–2022)
-- Analytical Question: How did annual movie release counts trend over the past decade?
-- Demonstrates: WHERE range filtering, GROUP BY, aggregations.
-- ------------------------------------------------------------------------------
SELECT 
    Release_Year,
    COUNT(*) AS annual_releases,
    ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS avg_rating,
    ROUND(AVG(Popularity), 1) AS avg_popularity
FROM movies
WHERE Release_Year BETWEEN 2010 AND 2022
GROUP BY Release_Year
ORDER BY Release_Year ASC;


-- ------------------------------------------------------------------------------
-- QUERY 5: Year-over-Year (YoY) Growth Rate Around External Shocks (2015–2021)
-- Analytical Question: What was the annual percentage growth leading up to the 
-- 2020 pandemic and during the 2021 backlog recovery?
-- Demonstrates: Common Table Expression (CTE) and LAG() window function.
-- ------------------------------------------------------------------------------
WITH annual_counts AS (
    SELECT 
        Release_Year,
        COUNT(*) AS releases
    FROM movies
    WHERE Release_Year BETWEEN 2014 AND 2022
    GROUP BY Release_Year
),
yoy_calculations AS (
    SELECT 
        Release_Year,
        releases,
        LAG(releases, 1) OVER (ORDER BY Release_Year) AS prev_year_releases,
        releases - LAG(releases, 1) OVER (ORDER BY Release_Year) AS net_change,
        ROUND(
            ((releases - LAG(releases, 1) OVER (ORDER BY Release_Year)) * 100.0) 
            / LAG(releases, 1) OVER (ORDER BY Release_Year), 
            2
        ) AS yoy_growth_pct
    FROM annual_counts
)
SELECT 
    Release_Year,
    releases,
    COALESCE(prev_year_releases, 0) AS prev_year_releases,
    COALESCE(net_change, 0) AS net_change,
    COALESCE(yoy_growth_pct, 0.0) AS yoy_growth_pct
FROM yoy_calculations
WHERE Release_Year >= 2015
ORDER BY Release_Year ASC;


-- ------------------------------------------------------------------------------
-- QUERY 6: Top 5 Highest-Rated Blockbusters (Minimum 1,000 Votes)
-- Analytical Question: Which films achieved the highest audience acclaim with
-- substantial consensus (at least 1,000 user reviews)?
-- Demonstrates: Multi-condition WHERE filtering, ORDER BY multi-column sort.
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- QUERY 7: Top 5 Most Common Genre Pairings (Multi-Genre Synergy)
-- Analytical Question: Which distinct genres are most frequently paired together
-- on the same film?
-- Demonstrates: Relational self-join with inequality condition.
-- ------------------------------------------------------------------------------
SELECT 
    g1.genre AS genre_a,
    g2.genre AS genre_b,
    COUNT(*) AS pair_frequency
FROM movie_genres g1
JOIN movie_genres g2 
  ON g1.movie_id = g2.movie_id 
 AND g1.genre < g2.genre
GROUP BY g1.genre, g2.genre
ORDER BY pair_frequency DESC
LIMIT 5;
