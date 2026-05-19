import pickle
import random
import requests
import streamlit as st
import streamlit.components.v1 as components
##
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=" – Movie Recommender by Farzam Ameer",
    page_icon="🎬",
    layout="wide",
)

# ── Global Streamlit chrome CSS only ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0a0a0a !important;
    color: #e5e5e5 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Selectbox */
.stSelectbox > label { display: none !important; }
div[data-baseweb="select"] > div {
    background: #161616 !important;
    border: 1.5px solid #2c2c2c !important;
    border-radius: 8px !important;
    color: #e5e5e5 !important;
    font-size: 15px !important;
    min-height: 52px !important;
    padding: 0 16px !important;
    transition: border-color 0.2s !important;
}
div[data-baseweb="select"] > div:hover  { border-color: #444 !important; }
div[data-baseweb="select"] > div:focus-within { border-color: #e50914 !important; }
div[data-baseweb="select"] svg { fill: #555 !important; }
[data-baseweb="popover"] ul, [data-baseweb="menu"] {
    background: #161616 !important;
    border: 1px solid #2c2c2c !important;
    border-radius: 8px !important;
}
[role="option"] {
    background: #161616 !important;
    color: #ccc !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
}
[role="option"]:hover, [aria-selected="true"] {
    background: #222 !important; color: #fff !important;
}

/* Button */
.stButton > button {
    background: #e50914 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    height: 52px !important;
    width: 100% !important;
    letter-spacing: 0.8px !important;
    transition: background 0.15s, transform 0.1s !important;
}
.stButton > button:hover  { background: #ff0a16 !important; }
.stButton > button:active { transform: scale(0.97) !important; }

/* Spinner */
.stSpinner > div { border-top-color: #e50914 !important; }

/* iframe seamless */
iframe { display: block; border: none; background: transparent; }
</style>
""", unsafe_allow_html=True)


# ── Card CSS shared across all iframes ────────────────────────────────────────
CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0a0a0a; font-family: 'DM Sans', sans-serif; }
.nf-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    padding: 0 0 8px;
}
.nf-card {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    background: #141414;
    border: 1px solid #1e1e1e;
    transition: transform 0.28s cubic-bezier(.25,.46,.45,.94),
                box-shadow 0.28s ease, border-color 0.2s;
    cursor: pointer;
}
.nf-card:hover {
    transform: translateY(-6px) scale(1.03);
    box-shadow: 0 20px 56px rgba(0,0,0,0.9), 0 0 0 1px #333;
    border-color: #2e2e2e;
    z-index: 10;
}
.nf-card img {
    width: 100%;
    display: block;
    aspect-ratio: 2/3;
    object-fit: cover;
}
.nf-card-overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.97) 0%, rgba(0,0,0,0.5) 55%, transparent 100%);
    padding: 48px 14px 14px;
    opacity: 0;
    transition: opacity 0.22s ease;
}
.nf-card:hover .nf-card-overlay { opacity: 1; }
.nf-card-match {
    font-size: 10px; color: #4ade80; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px;
}
.nf-card-title-hover { font-size: 13px; font-weight: 600; color: #fff; line-height: 1.3; }
.nf-rank-badge {
    position: absolute; top: 10px; left: 10px;
    background: rgba(229,9,20,0.92); color: #fff;
    font-size: 10px; font-weight: 700; padding: 3px 8px;
    border-radius: 4px; letter-spacing: 0.8px;
}
.nf-trending-badge {
    position: absolute; top: 10px; right: 10px;
    background: rgba(250,175,0,0.9); color: #1a1000;
    font-size: 9px; font-weight: 700; padding: 3px 7px;
    border-radius: 4px; letter-spacing: 1px; text-transform: uppercase;
}
.nf-card-footer { padding: 10px 12px 12px; border-top: 1px solid #222; }
.nf-card-name {
    font-size: 12px; font-weight: 500; color: #c0c0c0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 3px;
}
.nf-card-sub { font-size: 10px; color: #484848; font-weight: 300; }
</style>
"""


# ── Core logic ─────────────────────────────────────────────────────────────────
def fetch_poster(movie_id):
    try:
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
        data = requests.get(url, timeout=5).json()
        pp = data.get('poster_path')
        if pp:
            return "https://image.tmdb.org/t/p/w500/" + pp
    except Exception:
        pass
    return None


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        if poster:
            posters.append(poster)
            names.append(movies.iloc[i[0]].title)
    return names, posters


def get_random_movies(n=5):
    sample = movies.sample(n * 2)
    names, posters = [], []
    for _, row in sample.iterrows():
        if len(names) >= n:
            break
        poster = fetch_poster(row['movie_id'])
        if poster:
            names.append(row['title'])
            posters.append(poster)
    return names[:n], posters[:n]


def build_grid_html(names, posters, badge_label="Match", badge_values=None, show_trending=False):
    """Return a full self-contained HTML page for use inside an iframe."""
    default_badges = [98, 95, 93, 91, 89]
    cards = ""
    for idx, (name, poster) in enumerate(zip(names, posters)):
        bval = badge_values[idx] if badge_values else default_badges[idx]
        rank = f"#{idx+1:02d}"
        trending = '<div class="nf-trending-badge">Trending</div>' if show_trending else ""
        sub = "Top similarity match" if badge_label == "Match" else "Popular right now"
        cards += f"""
        <div class="nf-card">
            <img src="{poster}" alt="" loading="lazy" />
            <div class="nf-rank-badge">{rank}</div>
            {trending}
            <div class="nf-card-overlay">
                <div class="nf-card-match">{bval}% {badge_label}</div>
                <div class="nf-card-title-hover">{name}</div>
            </div>
            <div class="nf-card-footer">
                <div class="nf-card-name">{name}</div>
                <div class="nf-card-sub">{sub}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">{CARD_CSS}</head>
<body>
<div class="nf-grid">{cards}</div>
</body></html>"""


def render_card_grid(names, posters, badge_label="Match", badge_values=None, show_trending=False):
    html = build_grid_html(names, posters, badge_label, badge_values, show_trending)
    # height: poster aspect-ratio 2:3, ~220px poster + ~55px footer per card at typical width
    components.html(html, height=360, scrolling=False)


# ── Load models ────────────────────────────────────────────────────────────────
movies     = pickle.load(open('models/movies.pkl', 'rb'))
similarity = pickle.load(open('models/similarity.pkl', 'rb'))
movie_list = movies['title'].values

if 'random_names' not in st.session_state:
    with st.spinner("Loading featured movies…"):
        rn, rp = get_random_movies(5)
        st.session_state.random_names   = rn
        st.session_state.random_posters = rp


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(180deg,#1c0000 0%,#0a0a0a 100%);
    padding: 24px 52px 18px;
    border-bottom: 1px solid #1c1c1c;
    display: flex; align-items: flex-end; gap: 20px;
    margin-bottom: 0;
">
    <span style="font-family:'Bebas Neue',sans-serif;font-size:54px;color:#e50914;letter-spacing:4px;line-height:1;">MovieFlix</span>
    <span style="font-size:11px;color:#555;letter-spacing:2px;text-transform:uppercase;padding-bottom:8px;font-weight:300;">
        Movie Recommender &nbsp;·&nbsp; By Farzam Ameer
    </span>
</div>
""", unsafe_allow_html=True)

# ── Search row ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

col_l, col_sel, col_gap, col_btn, col_r = st.columns([0.5, 7, 0.15, 1.5, 0.5])
with col_sel:
    st.markdown("<p style='font-size:10px;text-transform:uppercase;letter-spacing:3px;color:#444;margin-bottom:8px;font-weight:500;'>Type or select a movie you love</p>", unsafe_allow_html=True)
    selected_movie = st.selectbox(label="movie_select", options=movie_list, index=0)
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    recommend_clicked = st.button("▶  Recommend")

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── Divider helper ────────────────────────────────────────────────────────────
def divider():
    st.markdown("<hr style='border:none;border-top:1px solid #1c1c1c;margin:0 52px;'>", unsafe_allow_html=True)

def section_title(html):
    st.markdown(f"<div style='padding:28px 52px 16px;font-size:20px;font-weight:600;color:#e5e5e5;font-family:DM Sans,sans-serif;'>{html}</div>", unsafe_allow_html=True)

def grid_padding():
    st.markdown("<div style='padding:0 44px'>", unsafe_allow_html=True)


# ── Results ───────────────────────────────────────────────────────────────────
if recommend_clicked:
    with st.spinner("Finding your next obsession…"):
        rec_names, rec_posters = recommend(selected_movie)

    if rec_names:
        divider()
        section_title(f'Because you watched &nbsp;<span style="color:#e50914">{selected_movie}</span><span style="font-size:12px;color:#555;font-weight:300;margin-left:12px;">Top 5 picks</span>')
        with st.container():
            st.markdown("<div style='padding:0 44px;'>", unsafe_allow_html=True)
            render_card_grid(rec_names, rec_posters, badge_label="Match")
            st.markdown("</div>", unsafe_allow_html=True)

        divider()
        section_title('Trending Today <span style="font-size:12px;color:#555;font-weight:300;margin-left:12px;">Refreshes each session</span>')
        with st.container():
            st.markdown("<div style='padding:0 44px;'>", unsafe_allow_html=True)
            render_card_grid(
                st.session_state.random_names,
                st.session_state.random_posters,
                badge_label="Trending",
                badge_values=[random.randint(80, 97) for _ in range(5)],
                show_trending=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Couldn't load recommendations. Check your internet connection.")

else:
    divider()
    section_title('Trending Today <span style="font-size:12px;color:#555;font-weight:300;margin-left:12px;">Refreshes each session</span>')
    with st.container():
        st.markdown("<div style='padding:0 44px;'>", unsafe_allow_html=True)
        render_card_grid(
            st.session_state.random_names,
            st.session_state.random_posters,
            badge_label="Trending",
            badge_values=[random.randint(80, 97) for _ in range(5)],
            show_trending=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)