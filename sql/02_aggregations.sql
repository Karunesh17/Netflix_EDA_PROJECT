-- ==============================================================================
-- SQL Analytics File 2: Aggregations & Conditional Logic
-- Database: movies_analytics.db (SQLite)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Executive KPI Summary & Rating Integrity Segregation
-- Business Question: What is the overall catalog volume, and how does segregating
-- unrated titles (Vote_Count == 0) impact our baseline average rating?
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_catalog_titles,
    COUNT(DISTINCT Title) AS unique_titles,
    SUM(CASE WHEN Rating_Status = 'Unrated' THEN 1 ELSE 0 END) AS unrated_titles_count,
    SUM(CASE WHEN Rating_Status = 'Rated' THEN 1 ELSE 0 END) AS rated_titles_count,
    ROUND(AVG(Vote_Average), 2) AS unadjusted_avg_rating,
    ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS clean_rated_avg_rating,
    ROUND(AVG(Popularity), 2) AS avg_popularity,
    ROUND(AVG(Vote_Count), 1) AS avg_vote_count,
    MIN(Release_Year) AS earliest_release_year,
    MAX(Release_Year) AS latest_release_year
FROM movies;


-- ------------------------------------------------------------------------------
-- QUERY 2: Language Market Penetration & Regional Share Analysis
-- Business Question: How is the catalog distributed across major linguistic
-- markets, and what percentage of content represents international non-English cinema?
-- ------------------------------------------------------------------------------
WITH language_classification AS (
    SELECT 
        movie_id,
        Title,
        Original_Language,
        CASE 
            WHEN Original_Language = 'en' THEN 'English (US/UK/CAN/AUS)'
            WHEN Original_Language = 'ja' THEN 'Japanese (Anime / Cinema)'
            WHEN Original_Language = 'es' THEN 'Spanish (LATAM / Spain)'
            WHEN Original_Language = 'fr' THEN 'French'
            WHEN Original_Language = 'ko' THEN 'Korean (K-Drama / Cinema)'
            WHEN Original_Language = 'zh' OR Original_Language = 'cn' THEN 'Chinese (Mandarin / Cantonese)'
            WHEN Original_Language = 'it' THEN 'Italian'
            WHEN Original_Language = 'de' THEN 'German'
            ELSE 'Other International (34 Languages)'
        END AS language_tier
    FROM movies
),
total_count AS (
    SELECT COUNT(*) AS grand_total FROM movies
)
SELECT 
    lc.language_tier,
    COUNT(*) AS title_count,
    ROUND((COUNT(*) * 100.0) / tc.grand_total, 2) AS catalog_share_pct
FROM language_classification lc
CROSS JOIN total_count tc
GROUP BY lc.language_tier, tc.grand_total
ORDER BY title_count DESC;
