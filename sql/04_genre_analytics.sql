-- ==============================================================================
-- SQL Analytics File 4: Normalized Multi-Label Genre Intelligence
-- Database: movies_analytics.db (SQLite)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 6: Normalized Genre Portfolio Volume & Dual Denominators
-- Business Question: What is the true ranking of all 19 genres by total tag
-- occurrences versus film title penetration?
-- Demonstrates: Relational JOIN, dual CTE denominators, aggregations.
-- ------------------------------------------------------------------------------
WITH genre_aggregations AS (
    SELECT 
        mg.genre,
        COUNT(DISTINCT m.movie_id) AS title_count,
        ROUND(AVG(CASE WHEN m.Rating_Status = 'Rated' THEN m.Vote_Average ELSE NULL END), 2) AS avg_genre_rating,
        ROUND(AVG(m.Popularity), 2) AS avg_genre_popularity
    FROM movie_genres mg
    JOIN movies m ON mg.movie_id = m.movie_id
    GROUP BY mg.genre
),
totals AS (
    SELECT 
        (SELECT COUNT(*) FROM movie_genres) AS total_genre_tags,
        (SELECT COUNT(*) FROM movies) AS total_titles
)
SELECT 
    ga.genre,
    ga.title_count AS tag_count,
    ROUND((ga.title_count * 100.0) / t.total_genre_tags, 2) AS share_of_genre_tags_pct,
    ROUND((ga.title_count * 100.0) / t.total_titles, 2) AS title_penetration_pct,
    ga.avg_genre_rating,
    ga.avg_genre_popularity
FROM genre_aggregations ga
CROSS JOIN totals t
ORDER BY ga.title_count DESC;


-- ------------------------------------------------------------------------------
-- QUERY 7: Genre Co-Occurrence Matrix (Top 10 Genre Pairings)
-- Business Question: Which distinct genres are most frequently paired together
-- on the same film (multi-genre synergy)?
-- Demonstrates: Self-JOIN on bridge table with inequality condition (g1.genre < g2.genre).
-- ------------------------------------------------------------------------------
WITH genre_pairs AS (
    SELECT 
        g1.genre AS genre_a,
        g2.genre AS genre_b,
        COUNT(*) AS pair_frequency
    FROM movie_genres g1
    JOIN movie_genres g2 
      ON g1.movie_id = g2.movie_id 
     AND g1.genre < g2.genre
    GROUP BY g1.genre, g2.genre
),
total_movies AS (
    SELECT COUNT(*) AS total_films FROM movies
)
SELECT 
    gp.genre_a,
    gp.genre_b,
    gp.pair_frequency,
    ROUND((gp.pair_frequency * 100.0) / tm.total_films, 2) AS pair_title_penetration_pct
FROM genre_pairs gp
CROSS JOIN total_movies tm
ORDER BY gp.pair_frequency DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 8: Commercial Blockbuster vs Critical Acclaim Divergence
-- Business Question: Which movies exhibit significant divergence between mass
-- commercial popularity and audience acclaim (High Popularity vs Moderate Score)?
-- Demonstrates: Multi-tiered CASE WHEN, quartile thresholds, compound filtering.
-- ------------------------------------------------------------------------------
WITH threshold_metrics AS (
    SELECT 
        Title,
        Release_Year,
        Popularity,
        Vote_Count,
        Vote_Average,
        Original_Language,
        Genre,
        CASE 
            WHEN Popularity >= 100.0 AND Vote_Average >= 8.0 THEN 'Universal Hit (High Popularity + Acclaimed)'
            WHEN Popularity >= 100.0 AND Vote_Average < 6.5 THEN 'Commercial Driver (High Popularity + Low/Mid Score)'
            WHEN Popularity < 30.0 AND Vote_Average >= 8.0 AND Vote_Count >= 500 THEN 'Hidden Critical Gem (Niche + Acclaimed)'
            ELSE 'Standard Catalog'
        END AS performance_quadrant
    FROM movies
    WHERE Rating_Status = 'Rated'
)
SELECT 
    performance_quadrant,
    COUNT(*) AS movie_count,
    ROUND(AVG(Popularity), 2) AS avg_popularity,
    ROUND(AVG(Vote_Average), 2) AS avg_score,
    ROUND(AVG(Vote_Count), 0) AS avg_votes
FROM threshold_metrics
WHERE performance_quadrant != 'Standard Catalog'
GROUP BY performance_quadrant
ORDER BY movie_count DESC;
