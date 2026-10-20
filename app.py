import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# Netflix Content Explorer — interactive portfolio dashboard
# Run: streamlit run app.py
# Keep netflix_titles.csv in the same folder as this file.
# ------------------------------------------------------------

st.set_page_config(
    page_title="Netflix Content Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG = "#090B10"
PANEL = "#141923"
PANEL_2 = "#1B2230"
TEXT = "#F4F6FA"
MUTED = "#A6AFBF"
RED = "#E50914"
TEAL = "#4DD6C8"
GOLD = "#F6C85F"
BLUE = "#7AA7FF"

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
      html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
      .stApp {{ background: radial-gradient(ellipse at top right, #25202b 0%, {BG} 43%, #08090d 100%); color: {TEXT}; }}
      [data-testid="stSidebar"] {{ background: #10141d; border-right: 1px solid #272d39; }}
      [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
      h1, h2, h3 {{ font-family: 'Outfit', sans-serif !important; color: {TEXT} !important; }}
      .hero {{ padding: 1.2rem 1.5rem 1.4rem 1.5rem; border: 1px solid #303746; border-radius: 20px;
               background: linear-gradient(115deg, rgba(229,9,20,.22), rgba(20,25,35,.94) 48%, rgba(77,214,200,.08));
               margin-bottom: 1.1rem; }}
      .eyebrow {{ color: {TEAL}; text-transform: uppercase; letter-spacing: .18em; font-size: .74rem; font-weight: 700; }}
      .hero-title {{ font-family: 'Outfit', sans-serif; font-size: 2.35rem; font-weight: 800; line-height: 1.1; margin: .35rem 0 .5rem 0; }}
      .hero-sub {{ color: {MUTED}; font-size: 1rem; max-width: 780px; }}
      .metric {{ background: linear-gradient(145deg, {PANEL_2}, {PANEL}); border: 1px solid #2b3342;
                 border-radius: 16px; padding: 1rem 1.1rem; min-height: 112px; }}
      .metric-label {{ color: {MUTED}; font-size: .82rem; font-weight: 600; }}
      .metric-value {{ color: {TEXT}; font-family: 'Outfit', sans-serif; font-size: 1.9rem; font-weight: 800; margin-top: .2rem; }}
      .metric-foot {{ color: {TEAL}; font-size: .76rem; margin-top: .1rem; }}
      .section-label {{ color: {TEAL}; font-size: .74rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }}
      .insight {{ background: #111923; border-left: 4px solid {RED}; border-radius: 8px; padding: .85rem 1rem; color: {TEXT}; }}
      div[data-testid="stPlotlyChart"] {{ background: rgba(20,25,35,.72); border: 1px solid #283140; border-radius: 15px; padding: .35rem; }}
      div[data-testid="stDataFrame"] {{ border: 1px solid #283140; border-radius: 12px; }}
      .small-muted {{ color: {MUTED}; font-size: .83rem; }}
      .stButton button, .stDownloadButton button {{ border-radius: 10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    # Standardize columns and safely parse dates.
    df.columns = [c.strip() for c in df.columns]
    for col in ["type", "title", "director", "cast", "country", "rating", "listed_in", "description"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce", format="mixed")
        df["year_added"] = df["date_added"].dt.year
        df["month_added"] = df["date_added"].dt.month
    if "release_year" in df.columns:
        df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    if "duration" in df.columns:
        df["duration_num"] = pd.to_numeric(df["duration"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    return df

try:
    df_all = load_data()
except FileNotFoundError:
    st.error("I couldn't find `netflix_titles.csv`. Put it in the same folder as `app.py`, then run the dashboard again.")
    st.stop()

# Sidebar filters
st.sidebar.markdown("## 🎛️ Dashboard controls")
st.sidebar.caption("Use the filters to explore the catalogue. All charts update together.")
types = sorted(df_all["type"].dropna().unique().tolist()) if "type" in df_all else []
selected_types = st.sidebar.multiselect("Content type", types, default=types)
years = df_all["release_year"].dropna()
if not years.empty:
    min_y, max_y = int(years.min()), int(years.max())
    year_range = st.sidebar.slider("Release year", min_y, max_y, (max(min_y, 2000), max_y))
else:
    year_range = (1900, 2100)
country_values = sorted({c.strip() for val in df_all.get("country", pd.Series(dtype=str)).dropna() for c in str(val).split(",") if c.strip() and c.strip() != "Unknown"})
selected_countries = st.sidebar.multiselect("Country (optional)", country_values, default=[])
rating_values = sorted([r for r in df_all.get("rating", pd.Series(dtype=str)).dropna().unique().tolist() if r != "Unknown"])
selected_ratings = st.sidebar.multiselect("Content rating (optional)", rating_values, default=[])
st.sidebar.markdown("---")
st.sidebar.caption("Portfolio project • Python • Pandas • Plotly • Streamlit")

filtered = df_all.copy()
if "type" in filtered and selected_types:
    filtered = filtered[filtered["type"].isin(selected_types)]
elif "type" in filtered and not selected_types:
    filtered = filtered.iloc[0:0]
if "release_year" in filtered:
    filtered = filtered[filtered["release_year"].between(year_range[0], year_range[1], inclusive="both")]
if selected_countries and "country" in filtered:
    pattern = "|".join([__import__("re").escape(c) for c in selected_countries])
    filtered = filtered[filtered["country"].str.contains(pattern, case=False, na=False)]
if selected_ratings and "rating" in filtered:
    filtered = filtered[filtered["rating"].isin(selected_ratings)]

# Hero
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Streaming intelligence · Portfolio dashboard</div>
      <div class="hero-title">NETFLIX <span style="color:#E50914">CONTENT</span> EXPLORER</div>
      <div class="hero-sub">Explore the catalogue, compare movies and TV shows, and uncover content trends. Adjust the filters on the left to make the whole dashboard respond to your questions.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Catalogue at a glance</div>', unsafe_allow_html=True)
total = len(filtered)
movies = int((filtered["type"] == "Movie").sum()) if "type" in filtered else 0
shows = int((filtered["type"] == "TV Show").sum()) if "type" in filtered else 0
countries_count = filtered["country"].nunique() if "country" in filtered else 0
avg_year = int(filtered["release_year"].dropna().median()) if "release_year" in filtered and filtered["release_year"].notna().any() else "—"
k1, k2, k3, k4, k5 = st.columns(5)
metrics = [
    (k1, "TITLES IN VIEW", f"{total:,}", "Matching current filters"),
    (k2, "MOVIES", f"{movies:,}", f"{(movies / total * 100):.1f}% of view" if total else "No matching titles"),
    (k3, "TV SHOWS", f"{shows:,}", f"{(shows / total * 100):.1f}% of view" if total else "No matching titles"),
    (k4, "COUNTRIES", f"{countries_count:,}", "Countries represented"),
    (k5, "MEDIAN RELEASE YEAR", str(avg_year), "Middle release year"),
]
for col, label, value, foot in metrics:
    with col:
        st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>', unsafe_allow_html=True)

st.write("")
if filtered.empty:
    st.warning("No titles match these filters. Try widening the release-year range or removing a filter.")
    st.stop()

# Charts
left, right = st.columns([1.05, 1.35], gap="large")
with left:
    st.markdown("### 🎬 Movies vs TV Shows")
    type_counts = filtered["type"].value_counts().rename_axis("Content type").reset_index(name="Titles")
    fig = px.pie(type_counts, names="Content type", values="Titles", hole=.68,
                 color="Content type", color_discrete_map={"Movie": RED, "TV Show": TEAL},
                 template="plotly_dark")
    fig.update_traces(textposition="inside", textinfo="percent", insidetextfont=dict(size=13, color="white"),
                      marker=dict(line=dict(color=BG, width=3)), hovertemplate="%{label}<br>%{value:,} titles (%{percent})<extra></extra>")
    fig.update_layout(height=340, margin=dict(l=10,r=10,t=15,b=10), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(orientation="h", y=-.08))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### 📈 Content released over time")
    if "release_year" in filtered:
        trend = filtered.dropna(subset=["release_year"]).groupby(["release_year", "type"]).size().reset_index(name="Titles")
        fig = px.area(trend, x="release_year", y="Titles", color="type",
                      color_discrete_map={"Movie": RED, "TV Show": TEAL}, template="plotly_dark",
                      labels={"release_year":"Release year", "Titles":"Titles", "type":"Content type"})
        fig.update_layout(height=340, margin=dict(l=10,r=10,t=15,b=10), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", legend_title_text="", hovermode="x unified")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#29313e")
        st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("### 🌍 Top countries")
    if "country" in filtered:
        country_counts = (filtered[filtered["country"] != "Unknown"]["country"]
                          .str.split(",").explode().str.strip().value_counts().head(10)
                          .sort_values().reset_index())
        country_counts.columns = ["Country", "Titles"]
        fig = px.bar(country_counts, x="Titles", y="Country", orientation="h", text="Titles",
                     color="Titles", color_continuous_scale=["#64202A", RED, GOLD], template="plotly_dark")
        fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>%{x:,} titles<extra></extra>")
        fig.update_layout(height=390, margin=dict(l=10,r=35,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, xaxis_title="Titles", yaxis_title="")
        fig.update_xaxes(gridcolor="#29313e")
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### 🧭 Most common genres")
    if "listed_in" in filtered:
        genres = (filtered[filtered["listed_in"] != "Unknown"]["listed_in"]
                  .str.split(",").explode().str.strip().value_counts().head(10)
                  .sort_values().reset_index())
        genres.columns = ["Genre", "Titles"]
        fig = px.bar(genres, x="Titles", y="Genre", orientation="h", text="Titles",
                     color="Titles", color_continuous_scale=["#17454A", TEAL, BLUE], template="plotly_dark")
        fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>%{x:,} titles<extra></extra>")
        fig.update_layout(height=390, margin=dict(l=10,r=35,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, xaxis_title="Titles", yaxis_title="")
        fig.update_xaxes(gridcolor="#29313e")
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2, gap="large")
with c3:
    st.markdown("### 🔞 Content ratings")
    if "rating" in filtered:
        ratings = filtered[filtered["rating"] != "Unknown"]["rating"].value_counts().head(12).sort_values().reset_index()
        ratings.columns = ["Rating", "Titles"]
        fig = px.bar(ratings, x="Titles", y="Rating", orientation="h", text="Titles",
                     color_discrete_sequence=[GOLD], template="plotly_dark")
        fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>%{x:,} titles<extra></extra>")
        fig.update_layout(height=360, margin=dict(l=10,r=30,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Titles", yaxis_title="")
        fig.update_xaxes(gridcolor="#29313e")
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

with c4:
    st.markdown("### 🗓️ Added to Netflix")
    if "year_added" in filtered:
        added = filtered.dropna(subset=["year_added"]).groupby("year_added").size().reset_index(name="Titles")
        fig = px.line(added, x="year_added", y="Titles", markers=True, template="plotly_dark")
        fig.update_traces(line=dict(color=TEAL, width=3), marker=dict(size=7, color=GOLD),
                          hovertemplate="Year %{x}<br>%{y:,} titles added<extra></extra>")
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Year added", yaxis_title="Titles")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#29313e")
        st.plotly_chart(fig, use_container_width=True)

# Dynamic findings
st.markdown("### 💡 What the current view tells us")
type_top = filtered["type"].value_counts().index[0] if "type" in filtered and not filtered["type"].empty else "—"
latest_release = int(filtered["release_year"].max()) if "release_year" in filtered and filtered["release_year"].notna().any() else "—"
top_genre = "—"
if "listed_in" in filtered:
    gs = filtered.loc[filtered["listed_in"] != "Unknown", "listed_in"].str.split(",").explode().str.strip().value_counts()
    if not gs.empty:
        top_genre = gs.index[0]
top_country = "—"
if "country" in filtered:
    cs = filtered.loc[filtered["country"] != "Unknown", "country"].str.split(",").explode().str.strip().value_counts()
    if not cs.empty:
        top_country = cs.index[0]
st.markdown(
    f'<div class="insight">In the current filtered view, <b>{type_top}</b> is the most common format. '
    f'The most frequent listed genre is <b>{top_genre}</b>, and <b>{top_country}</b> appears most often in country credits. '
    f'The latest release year represented is <b>{latest_release}</b>. Use the sidebar filters to test how these findings change.</div>',
    unsafe_allow_html=True,
)
st.caption("Note: country and genre credits can contain multiple comma-separated values, so their chart counts are credit/genre occurrences, not mutually exclusive title totals.")

# Data explorer and export
with st.expander("🔎 Explore matching titles and download the filtered data"):
    search_text = st.text_input("Search title, director, cast, or description", placeholder="Try a title or actor name…")
    table_df = filtered.copy()
    if search_text:
        searchable = [c for c in ["title", "director", "cast", "description"] if c in table_df.columns]
        mask = pd.Series(False, index=table_df.index)
        for col in searchable:
            mask = mask | table_df[col].astype(str).str.contains(search_text, case=False, na=False)
        table_df = table_df[mask]
    display_cols = [c for c in ["title", "type", "release_year", "rating", "duration", "country", "listed_in", "date_added"] if c in table_df.columns]
    st.dataframe(table_df[display_cols], use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered CSV",
        data=table_df.to_csv(index=False).encode("utf-8"),
        file_name="netflix_filtered_titles.csv",
        mime="text/csv",
    )

st.markdown("---")
st.markdown('<div class="small-muted">Built with Python · Pandas · Plotly · Streamlit | Dataset: Netflix titles catalogue (public dataset)</div>', unsafe_allow_html=True)
