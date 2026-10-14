"""
dashboard/app.py
Interactive movie data dashboard built with Streamlit and Plotly.
I created this to visualize trends in movie releases, genres, languages, and audience ratings.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="TMDb Movie Data Analysis | Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-title {
        color: #6c757d;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #212529;
        font-size: 26px;
        font-weight: 700;
        margin-top: 4px;
    }
    .callout-box {
        background-color: #e8f4fd;
        border-left: 4px solid #1976d2;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        margin-bottom: 16px;
        font-size: 14px;
        color: #0d47a1;
    }
</style>
""", unsafe_allow_html=True)

# 3. Data Loading with Streamlit Caching
@st.cache_data
def load_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    movies_path = os.path.join(base_dir, "data", "movies_cleaned.csv")
    genres_path = os.path.join(base_dir, "data", "movie_genres.csv")
    
    if not os.path.exists(movies_path) or not os.path.exists(genres_path):
        st.error("Processed data files not found in data/ directory. Please run data preparation first.")
        st.stop()
        
    df_movies = pd.read_csv(movies_path)
    df_genres = pd.read_csv(genres_path)
    return df_movies, df_genres

df_movies, df_genres = load_data()

# 4. Sidebar Controls (3 Filters)
with st.sidebar:
    st.title("🎬 Filter Catalog")
    st.markdown("Customize the dashboard view:")
    st.markdown("---")
    
    # 1. Release Year Range
    min_yr = int(df_movies['Release_Year'].min())
    max_yr = int(df_movies['Release_Year'].max())
    year_range = st.slider(
        "Release Year Range",
        min_value=min_yr,
        max_value=max_yr,
        value=(1980, max_yr)
    )
    
    # 2. Genre Filter
    available_genres = sorted(df_genres['genre'].unique())
    selected_genres = st.multiselect(
        "Filter by Genre",
        options=available_genres,
        default=[]
    )
    
    # 3. Language Filter
    top_langs = df_movies['Original_Language'].value_counts().head(10).index.tolist()
    lang_options = ["All Languages"] + top_langs
    selected_lang = st.selectbox(
        "Filter by Language",
        options=lang_options,
        index=0
    )
    
    st.markdown("---")
    st.caption("Dataset: 9,827 movies from The Movie Database (TMDb).")
    st.caption("Built with Python, Pandas, Streamlit & Plotly.")

# 5. Apply Filters
filtered_df = df_movies[
    (df_movies['Release_Year'] >= year_range[0]) & 
    (df_movies['Release_Year'] <= year_range[1])
]

if selected_lang != "All Languages":
    filtered_df = filtered_df[filtered_df['Original_Language'] == selected_lang]

if selected_genres:
    matching_ids = df_genres[df_genres['genre'].isin(selected_genres)]['movie_id'].unique()
    filtered_df = filtered_df[filtered_df['movie_id'].isin(matching_ids)]

# Filtered genres
filtered_genre_df = df_genres[df_genres['movie_id'].isin(filtered_df['movie_id'])]

# 6. Main Dashboard View
st.title("TMDb Movie Data Explorer")
st.markdown("""
<div class="callout-box">
    I built this dashboard to interactively explore 9,827 movies from TMDb.
    Use the sidebar filters to slice the data by release years, genres, or languages, and see how the metrics and charts update.
</div>
""", unsafe_allow_html=True)

# 7. KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Movies</div>
        <div class="metric-value">{len(filtered_df):,}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Distinct Genres</div>
        <div class="metric-value">{filtered_genre_df['genre'].nunique()}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    rated_sub = filtered_df[filtered_df['Rating_Status'] == 'Rated']
    avg_score = rated_sub['Vote_Average'].mean() if len(rated_sub) > 0 else np.nan
    score_str = f"{avg_score:.2f} / 10" if not np.isnan(avg_score) else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg Rating (Rated Titles)</div>
        <div class="metric-value">{score_str}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Original Languages</div>
        <div class="metric-value">{filtered_df['Original_Language'].nunique()}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 8. Charts Row 1: Top 10 Genres & Release Year Timeline
col_row1_a, col_row1_b = st.columns(2)

with col_row1_a:
    st.subheader("Top 10 Genres (Title Penetration %)")
    if len(filtered_df) > 0 and len(filtered_genre_df) > 0:
        genre_summary = filtered_genre_df['genre'].value_counts().head(10).reset_index()
        genre_summary.columns = ['Genre', 'Movie_Count']
        genre_summary['Penetration_Pct'] = (genre_summary['Movie_Count'] / len(filtered_df)) * 100.0
        genre_summary = genre_summary.sort_values('Penetration_Pct', ascending=True)
        
        fig_genre = px.bar(
            genre_summary,
            x='Penetration_Pct',
            y='Genre',
            orientation='h',
            text=genre_summary['Penetration_Pct'].apply(lambda x: f"{x:.1f}%"),
            color='Penetration_Pct',
            color_continuous_scale='Blues'
        )
        fig_genre.update_layout(xaxis_title="Percentage of Movies (%)", yaxis_title="Genre", height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_genre, use_container_width=True)
    else:
        st.info("No records match the current filter selection.")

with col_row1_b:
    st.subheader("Movies Released by Year")
    if len(filtered_df) > 0:
        yearly_counts = filtered_df['Release_Year'].value_counts().sort_index().reset_index()
        yearly_counts.columns = ['Release_Year', 'Movie_Count']
        
        fig_year = px.line(
            yearly_counts,
            x='Release_Year',
            y='Movie_Count',
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#1f77b4']
        )
        fig_year.update_layout(xaxis_title="Release Year", yaxis_title="Releases", height=380)
        st.plotly_chart(fig_year, use_container_width=True)
    else:
        st.info("No records match the current filter selection.")

# 9. Charts Row 2: Top Languages & Rating Distribution
col_row2_a, col_row2_b = st.columns(2)

with col_row2_a:
    st.subheader("Top Original Languages")
    if len(filtered_df) > 0:
        lang_counts = filtered_df['Original_Language'].value_counts().head(7).reset_index()
        lang_counts.columns = ['Language', 'Count']
        fig_lang = px.pie(
            lang_counts,
            names='Language',
            values='Count',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_lang.update_layout(height=360, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_lang, use_container_width=True)
    else:
        st.info("No records match the current filter selection.")

with col_row2_b:
    st.subheader("Audience Ratings Distribution")
    if len(rated_sub) > 0:
        fig_hist = px.histogram(
            rated_sub,
            x='Vote_Average',
            nbins=25,
            color_discrete_sequence=['#2ca02c'],
            opacity=0.8
        )
        fig_hist.add_vline(x=rated_sub['Vote_Average'].mean(), line_dash="dash", line_color="red", annotation_text=f"Mean: {rated_sub['Vote_Average'].mean():.2f}")
        fig_hist.update_layout(xaxis_title="Vote Average (0 to 10)", yaxis_title="Number of Movies", height=360)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No rated records match the current filter selection.")

# 10. Chart 5: Popularity vs. Audience Rating
st.subheader("Popularity vs. Audience Rating")
if len(rated_sub) > 0:
    plot_sample = rated_sub.sample(min(2000, len(rated_sub)), random_state=42)
    fig_scatter = px.scatter(
        plot_sample,
        x='Vote_Average',
        y='Popularity',
        size='Vote_Count',
        hover_name='Title',
        hover_data=['Release_Year', 'Original_Language'],
        log_y=True,
        opacity=0.6,
        color_discrete_sequence=['#9467bd']
    )
    fig_scatter.update_layout(
        xaxis_title="Vote Average (0 to 10)",
        yaxis_title="Popularity (Log Scale)",
        height=420
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("Spearman rank correlation is +0.13, showing that more popular or heavily marketed movies do not always have higher audience ratings.")
else:
    st.info("No records to display for scatter analysis.")

# 11. Data Table View
with st.expander("📋 View Sample Filtered Movies Data"):
    st.dataframe(
        filtered_df[['Title', 'Release_Year', 'Original_Language', 'Genre', 'Popularity', 'Vote_Average', 'Vote_Count']].head(50),
        use_container_width=True
    )
