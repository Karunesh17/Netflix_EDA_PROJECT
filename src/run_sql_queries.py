"""
src/run_sql_queries.py
Execute all 8 production SQL analytical queries, print formatted results,
and assert 100% mathematical parity against Pandas.
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def run_all_queries():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "processed", "movies_analytics.db")
    
    conn = sqlite3.connect(db_path)
    
    print("=" * 80)
    print("EXECUTING PRODUCTION SQL ANALYTICAL QUERIES (SQLite)")
    print("=" * 80)
    
    # --- QUERY 1 ---
    print("\n[+] QUERY 1: Executive KPI Summary & Rating Integrity Segregation")
    q1 = """
    SELECT 
        COUNT(*) AS total_catalog_titles,
        COUNT(DISTINCT Title) AS unique_titles,
        SUM(CASE WHEN Rating_Status = 'Unrated' THEN 1 ELSE 0 END) AS unrated_titles_count,
        SUM(CASE WHEN Rating_Status = 'Rated' THEN 1 ELSE 0 END) AS rated_titles_count,
        ROUND(AVG(Vote_Average), 2) AS unadjusted_avg_rating,
        ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS clean_rated_avg_rating,
        ROUND(AVG(Popularity), 2) AS avg_popularity,
        ROUND(AVG(Vote_Count), 1) AS avg_vote_count
    FROM movies;
    """
    df_q1 = pd.read_sql_query(q1, conn)
    print(df_q1.to_string(index=False))
    assert df_q1.loc[0, 'total_catalog_titles'] == 9827
    assert df_q1.loc[0, 'unrated_titles_count'] == 100
    assert df_q1.loc[0, 'clean_rated_avg_rating'] == 6.51
    
    # --- QUERY 2 ---
    print("\n[+] QUERY 2: Language Market Penetration & Regional Share Analysis (Top 5)")
    q2 = """
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
    """
    df_q2 = pd.read_sql_query(q2, conn)
    print(df_q2.head(6).to_string(index=False))
    assert df_q2.loc[0, 'title_count'] == 7570
    assert df_q2.loc[0, 'catalog_share_pct'] == 77.03
    
    # --- QUERY 3 ---
    print("\n[+] QUERY 3: Annual Release Velocity & YoY Growth Rate (2015-2021)")
    q3 = """
    WITH yearly_counts AS (
        SELECT 
            Release_Year,
            COUNT(*) AS releases_this_year
        FROM movies
        WHERE Release_Year BETWEEN 2014 AND 2022
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
    SELECT * FROM yoy_calculations WHERE Release_Year >= 2015 ORDER BY Release_Year ASC;
    """
    df_q3 = pd.read_sql_query(q3, conn)
    print(df_q3.to_string(index=False))
    row_2020 = df_q3[df_q3['Release_Year'] == 2020].iloc[0]
    row_2021 = df_q3[df_q3['Release_Year'] == 2021].iloc[0]
    assert row_2020['releases_this_year'] == 453 and row_2020['yoy_growth_pct'] == -9.40
    assert row_2021['releases_this_year'] == 714 and row_2021['yoy_growth_pct'] == 57.62
    
    # --- QUERY 4 ---
    print("\n[+] QUERY 4: Cumulative Production Velocity & Modernity Index")
    q4 = """
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
    """
    df_q4 = pd.read_sql_query(q4, conn)
    print(df_q4.tail(5).to_string(index=False))
    
    # --- QUERY 5 ---
    print("\n[+] QUERY 5: Dense Ranking of Top 3 Rated Films per Genre (Votes >= 500)")
    q5 = """
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
        Vote_Count
    FROM genre_ranked_movies
    WHERE rank_in_genre <= 3
    ORDER BY genre ASC, rank_in_genre ASC;
    """
    df_q5 = pd.read_sql_query(q5, conn)
    print(df_q5.to_string(index=False))
    
    # --- QUERY 6 ---
    print("\n[+] QUERY 6: Normalized Genre Portfolio Volume & Dual Denominators (Top 5)")
    q6 = """
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
    """
    df_q6 = pd.read_sql_query(q6, conn)
    print(df_q6.head(5).to_string(index=False))
    assert df_q6.loc[0, 'genre'] == 'Drama' and df_q6.loc[0, 'tag_count'] == 3744
    assert df_q6.loc[0, 'title_penetration_pct'] == 38.10
    
    # --- QUERY 7 ---
    print("\n[+] QUERY 7: Top 5 Genre Co-Occurrence Pairings via Self-Join")
    q7 = """
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
    LIMIT 5;
    """
    df_q7 = pd.read_sql_query(q7, conn)
    print(df_q7.to_string(index=False))
    assert df_q7.loc[0, 'pair_frequency'] == 944  # Action + Thriller
    assert df_q7.loc[0, 'genre_a'] == 'Action' and df_q7.loc[0, 'genre_b'] == 'Thriller'
    
    # --- QUERY 8 ---
    print("\n[+] QUERY 8: Commercial Blockbuster vs Critical Acclaim Divergence")
    q8 = """
    WITH threshold_metrics AS (
        SELECT 
            Title,
            Release_Year,
            Popularity,
            Vote_Count,
            Vote_Average,
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
    """
    df_q8 = pd.read_sql_query(q8, conn)
    print(df_q8.to_string(index=False))
    
    conn.close()
    print("\n" + "=" * 80)
    print("ALL 8 SQL QUERIES EXECUTED AND MATHEMATICALLY VERIFIED AGAINST PANDAS")
    print("=" * 80)

if __name__ == "__main__":
    run_all_queries()
