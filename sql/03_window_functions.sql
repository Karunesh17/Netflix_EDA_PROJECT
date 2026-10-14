-- ==============================================================================
-- SQL Analytics File 3: Window Functions, Growth Velocity & Ranking
-- Database: movies_analytics.db (SQLite)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 3: Annual Release Velocity & Year-over-Year (YoY) Growth Rate
-- Business Question: What is the annual production velocity, and how did releases
-- fluctuate year-over-year between 2010 and 2022?
-- Demonstrates: CTEs, LAG() window function, conditional NULL handling.
-- ------------------------------------------------------------------------------
WITH yearly_counts AS (
    SELECT 
        Release_Year,
        COUNT(*) AS releases_this_year
    FROM movies
    WHERE Release_Year BETWEEN 2010 AND 2022
    GROUP BY Release_Year
),
yoy_calculations AS (
    SELECT 
        Release_Year,
        releases_this_year,
        LAG(releases_this_year, 1) OVER (ORDER BY Release_Year) AS prev_year_releases,
        releases_this_year - LAG(releases_this_year, 1) OVER (ORDER BY Release_Year) AS net_yoy_change,
        ROUND(
            ((releases_this_year - LAG(releases_this_year, 1) OVER (ORDER BY Release_Year)) * 100.0) 
            / LAG(releases_this_year, 1) OVER (ORDER BY Release_Year), 
            2
        ) AS yoy_growth_pct
    FROM yearly_counts
)
SELECT 
    Release_Year,
    releases_this_year,
    COALESCE(prev_year_releases, 0) AS prev_year_releases,
    COALESCE(net_yoy_change, 0) AS net_yoy_change,
    COALESCE(yoy_growth_pct, 0.0) AS yoy_growth_pct
FROM yoy_calculations
ORDER BY Release_Year ASC;


-- ------------------------------------------------------------------------------
-- QUERY 4: Cumulative Production Velocity & Catalog Modernity Index
-- Business Question: How concentrated is the movie portfolio toward modern releases?
-- Demonstrates: SUM() OVER (ORDER BY ...) cumulative window function.
-- ------------------------------------------------------------------------------
WITH decade_stats AS (
    SELECT 
        Decade_Label,
        Decade,
        COUNT(*) AS titles_in_decade
    FROM movies
    GROUP BY Decade_Label, Decade
),
total_titles AS (
    SELECT COUNT(*) AS total_catalog FROM movies
)
SELECT 
    ds.Decade_Label,
    ds.titles_in_decade,
    ROUND((ds.titles_in_decade * 100.0) / tt.total_catalog, 2) AS decade_share_pct,
    SUM(ds.titles_in_decade) OVER (ORDER BY ds.Decade ASC) AS cumulative_titles,
    ROUND(
        (SUM(ds.titles_in_decade) OVER (ORDER BY ds.Decade ASC) * 100.0) / tt.total_catalog, 
        2
    ) AS cumulative_share_pct
FROM decade_stats ds
CROSS JOIN total_titles tt
ORDER BY ds.Decade ASC;


-- ------------------------------------------------------------------------------
-- QUERY 5: Top 3 Acclaimed Films per Major Genre (Reliability Filter >= 500 Votes)
-- Business Question: Within each major genre, what are the top 3 highest-rated
-- films that have achieved substantial audience consensus (minimum 500 votes)?
-- Demonstrates: DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...), JOIN with bridge table.
-- ------------------------------------------------------------------------------
WITH genre_ranked_movies AS (
    SELECT 
        mg.genre,
        m.Title,
        m.Release_Year,
        m.Vote_Average,
        m.Vote_Count,
        m.Popularity,
        DENSE_RANK() OVER (
            PARTITION BY mg.genre 
            ORDER BY m.Vote_Average DESC, m.Vote_Count DESC
        ) AS rank_in_genre
    FROM movies m
    JOIN movie_genres mg ON m.movie_id = mg.movie_id
    WHERE m.Vote_Count >= 500
      AND mg.genre IN ('Action', 'Comedy', 'Drama', 'Science Fiction', 'Animation')
)
SELECT 
    genre,
    rank_in_genre,
    Title,
    Release_Year,
    Vote_Average,
    Vote_Count,
    Popularity
FROM genre_ranked_movies
WHERE rank_in_genre <= 3
ORDER BY genre ASC, rank_in_genre ASC;
