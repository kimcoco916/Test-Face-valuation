import streamlit as st

GOLD = "#D4AF37"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Serif+KR:wght@400;700&display=swap');

:root {
  --gold: #D4AF37;
  --gold-soft: #E9D18A;
  --navy: #0F1630;
  --navy-2: #1A2347;
  --navy-3: #243063;
  --ink: #F3EAD3;
  --muted: #B9B2A0;
}

html, body, [class*="css"], .stMarkdown, .stText, button, input, label {
  font-family: 'Gowun Batang', 'Noto Serif KR', serif !important;
}

.stApp {
  background:
    radial-gradient(circle at 20% 0%, rgba(212,175,55,0.10), transparent 40%),
    radial-gradient(circle at 100% 100%, rgba(80,100,200,0.15), transparent 45%),
    var(--navy);
}

.block-container { max-width: 860px; padding-top: 2.5rem; }

/* ---------- Header ---------- */
.hero { text-align: center; margin-bottom: 1.5rem; }
.hero h1 {
  font-size: 2.6rem; font-weight: 700; margin: 0;
  color: var(--gold);
  letter-spacing: 0.05em;
  text-shadow: 0 0 18px rgba(212,175,55,0.35);
}
.hero p { color: var(--muted); font-size: 1.1rem; margin-top: 0.4rem; }
.hero .line {
  width: 120px; height: 2px; margin: 1rem auto 0;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

/* ---------- Section titles ---------- */
.section-title {
  color: var(--gold-soft); font-size: 1.3rem; font-weight: 700;
  margin: 2rem 0 0.8rem; padding-left: 0.6rem;
  border-left: 3px solid var(--gold);
}

/* ---------- Upload / preview ---------- */
[data-testid="stFileUploaderDropzone"] {
  background: var(--navy-2);
  border: 1.5px dashed rgba(212,175,55,0.55);
  border-radius: 14px;
}
[data-testid="stImage"] img {
  border-radius: 16px;
  border: 2px solid var(--gold);
  box-shadow: 0 6px 24px rgba(0,0,0,0.45);
}

/* ---------- Buttons ---------- */
.stButton > button[kind="primary"], .stDownloadButton > button {
  background: linear-gradient(135deg, #E9C766, #B8901F);
  color: #1A1405 !important;
  border: none; border-radius: 999px;
  font-weight: 700; font-size: 1.1rem;
  padding: 0.7rem 1.5rem;
  box-shadow: 0 4px 18px rgba(212,175,55,0.35);
  transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(212,175,55,0.5);
}
.stButton > button[kind="primary"]:disabled {
  background: var(--navy-3); color: var(--muted) !important; box-shadow: none;
}

/* ---------- Cards ---------- */
.card {
  background: linear-gradient(160deg, var(--navy-2), #151D3D);
  border: 1px solid rgba(212,175,55,0.35);
  border-radius: 16px;
  padding: 1.1rem 1.2rem;
  box-shadow: 0 6px 22px rgba(0,0,0,0.35);
  color: var(--ink);
  line-height: 1.7;
}
.summary-card {
  text-align: center; padding: 1.6rem 1.4rem;
  border: 1.5px solid var(--gold);
  box-shadow: 0 0 28px rgba(212,175,55,0.22);
}
.summary-card .label { color: var(--gold); font-size: 0.95rem; letter-spacing: 0.2em; }
.summary-card .text { font-size: 1.45rem; font-weight: 700; margin-top: 0.5rem; color: #FFF6DC; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 0.3rem; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] {
  background: var(--navy-2); border-radius: 10px 10px 0 0;
  padding: 0.4rem 0.8rem; color: var(--muted);
}
.stTabs [aria-selected="true"] { color: var(--gold) !important; background: var(--navy-3); }
.stTabs [data-baseweb="tab-panel"] {
  background: var(--navy-2); border: 1px solid rgba(212,175,55,0.25);
  border-radius: 0 12px 12px 12px; padding: 1rem 1.2rem; line-height: 1.8;
}

/* ---------- Fortune grid ---------- */
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.9rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; }
.fortune-head { display: flex; justify-content: space-between; align-items: baseline; }
.fortune-name { font-weight: 700; font-size: 1.1rem; color: var(--gold-soft); }
.fortune-score { font-size: 1.5rem; font-weight: 700; color: var(--gold); }
.fortune-score small { font-size: 0.8rem; color: var(--muted); }
.bar { height: 8px; border-radius: 999px; background: rgba(255,255,255,0.08); margin: 0.5rem 0 0.7rem; overflow: hidden; }
.bar > span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #8C6A12, var(--gold), #F5DE8E); }
.fortune-text { font-size: 0.95rem; color: var(--ink); }

/* ---------- Pills ---------- */
.pills { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.pill {
  padding: 0.35rem 0.95rem; border-radius: 999px;
  border: 1px solid var(--gold); color: var(--gold-soft);
  background: rgba(212,175,55,0.10); font-weight: 700;
}

/* ---------- Lucky cards ---------- */
.lucky-card { text-align: center; }
.lucky-card .label { color: var(--muted); font-size: 0.9rem; }
.lucky-card .value { font-size: 1.3rem; font-weight: 700; color: #FFF6DC; margin-top: 0.4rem; }
.lucky-card .advice { font-size: 1rem; font-weight: 400; line-height: 1.6; }
.swatch {
  display: inline-block; width: 26px; height: 26px; border-radius: 50%;
  vertical-align: middle; margin-right: 0.4rem;
  border: 2px solid rgba(255,255,255,0.6);
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #141C3B, #0B1126);
  border-right: 1px solid rgba(212,175,55,0.25);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--gold); }

/* ---------- Footer ---------- */
.footer {
  text-align: center; color: var(--muted); font-size: 0.85rem;
  margin-top: 3rem; padding-top: 1rem;
  border-top: 1px solid rgba(212,175,55,0.2);
}

/* ---------- Mobile ---------- */
@media (max-width: 640px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.5rem; }
  .hero h1 { font-size: 2rem; }
  .summary-card .text { font-size: 1.2rem; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
