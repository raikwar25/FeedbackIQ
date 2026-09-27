
import os
import json
import re
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(
    page_title="FeedbackIQ",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
/* Page */
.stApp { background: #f4f7fb; color: #172033; }
.block-container { padding: 1.5rem 2.2rem 3rem; max-width: 1450px; }

/* Header */
.hero {
    padding: 30px 34px;
    border-radius: 22px;
    background: linear-gradient(135deg, #0f172a 0%, #172554 55%, #1e3a8a 100%);
    color: #fff;
    margin-bottom: 24px;
    box-shadow: 0 10px 28px rgba(15,23,42,.12);
}
.hero h1 { font-size: 44px; margin: 0 0 7px; letter-spacing: -1.5px; color:#fff; }
.hero p { font-size: 17px; margin: 0; color:#dbeafe; }
.eyebrow { font-size: 11px; font-weight:800; letter-spacing:1.7px; color:#93c5fd; text-transform:uppercase; margin-bottom:8px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * { color: #e5e7eb !important; }
[data-testid="stSidebar"] .stCaption { color:#94a3b8 !important; }
[data-testid="stSidebar"] hr { border-color:#334155; }
[data-testid="stSidebar"] .stButton > button {
    background:#2563eb; color:#fff !important; border:0;
}

/* Cards */
.metric-card {
    padding: 19px 20px;
    border: 1px solid #dbe3ef;
    border-radius: 16px;
    background: #ffffff;
    min-height: 112px;
    box-shadow: 0 5px 16px rgba(15,23,42,.055);
}
.metric-label { font-size:11px; font-weight:800; letter-spacing:.8px; color:#64748b; margin-bottom:8px; }
.metric-value { font-size:31px; font-weight:800; color:#0f172a; line-height:1.1; }
.metric-sub { font-size:12px; color:#64748b; margin-top:7px; }

/* Sections */
.section-title { font-size:22px; font-weight:800; color:#0f172a; margin:8px 0 12px; }
.theme-card {
    border:1px solid #dbe3ef; border-radius:14px; padding:16px 18px;
    margin-bottom:10px; background:#fff; box-shadow:0 3px 10px rgba(15,23,42,.04);
}
.theme-card strong { color:#0f172a; }
.pill {
    display:inline-block; padding:4px 9px; border-radius:999px;
    background:#eff6ff; color:#1d4ed8; font-size:11px; font-weight:750;
    margin-left:7px;
}
.insight {
    border:1px solid #bfdbfe; border-left:5px solid #2563eb;
    padding:18px 20px; background:#eff6ff; color:#172033;
    border-radius:14px; margin:8px 0 18px;
}

/* Upload area */
[data-testid="stFileUploader"] {
    background:#ffffff;
    border:2px dashed #cbd5e1;
    border-radius:16px;
    padding:8px;
}
[data-testid="stFileUploader"] section {
    background:#fff;
}
[data-testid="stFileUploaderDropzone"] {
    background:#f8fafc !important;
}


/* Streamlit messages: explicit dark text on light surfaces */
[data-testid="stAlert"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #172033 !important;
}
[data-testid="stAlert"] * {
    color: #172033 !important;
}
[data-testid="stAlert"] svg {
    color: #2563eb !important;
    fill: #2563eb !important;
}

/* Success message */
div[data-baseweb="notification"][kind="positive"],
div[data-baseweb="notification"][kind="positive"] * {
    color: #166534 !important;
}

/* Info message */
div[data-baseweb="notification"][kind="info"],
div[data-baseweb="notification"][kind="info"] * {
    color: #1e3a8a !important;
}

/* File uploader labels/help text */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span {
    color: #172033 !important;
}


/* Upload controls */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 12px !important;
    box-shadow: 0 4px 14px rgba(15,23,42,.05);
}
[data-testid="stFileUploader"] section {
    background: #f8fafc !important;
    border: 1px dashed #94a3b8 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] button {
    background: #2563eb !important;
    color: #ffffff !important;
    border: 0 !important;
    border-radius: 9px !important;
}
[data-testid="stFileUploader"] button:hover {
    background: #1d4ed8 !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p {
    color: #334155 !important;
}

/* Dashboard navigation: explicit dark text, no inherited theme colors */
.nav-heading {
    font-size: 13px;
    font-weight: 800;
    color: #475569;
    margin: 2px 0 8px;
    text-transform: uppercase;
    letter-spacing: .7px;
}
div[data-testid="stRadio"] > label {
    display: none !important;
}
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 13px !important;
    padding: 6px !important;
    margin-bottom: 20px !important;
}
div[data-testid="stRadio"] label {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 9px !important;
    padding: 10px 15px !important;
    min-height: 42px !important;
    cursor: pointer !important;
}
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label div {
    color: #111111 !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 750 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #111111 !important;
    border-color: #111111 !important;
}
div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label:has(input:checked) span,
div[data-testid="stRadio"] label:has(input:checked) div {
    color: #ffffff !important;
}
div[data-testid="stRadio"] input {
    accent-color: #2563eb !important;
}

/* Charts: use a clean card instead of Streamlit's dark chart surface */
div[data-testid="stVegaLiteChart"] {
    background: #ffffff !important;
    border: 1px solid #dbe3ef !important;
    border-radius: 16px !important;
    padding: 14px !important;
    box-shadow: 0 5px 16px rgba(15,23,42,.05) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #dbe3ef !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Buttons */
.stButton > button {
    border-radius:10px;
    min-height:44px;
    font-weight:700;
    border:1px solid #cbd5e1;
    background:#fff;
    color:#172033;
}
.stButton > button:hover {
    border-color:#2563eb;
    color:#1d4ed8;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight:700;
    color:#64748b;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color:#1d4ed8;
}

/* Expanders / info boxes */
[data-testid="stExpander"] {
    background:#fff;
    border:1px solid #dbe3ef;
    border-radius:13px;
}
[data-testid="stAlert"] { border-radius:12px; }

/* Flow */
.flow { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin:14px 0 2px; }
.flow span {
    padding:8px 12px; border-radius:9px; background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.16); font-size:12px; font-weight:700;
}
.flow b { color:#93c5fd; }

/* Mobile */
@media (max-width: 900px) {
    .block-container { padding:1rem; }
    .hero h1 { font-size:34px; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Demo data ----------
DEMO_FEEDBACK = [
    "Something is wrong with the payment.",
    "It just doesn't work when I try to pay.",
    "I was charged but the order didn't go through.",
    "The money disappeared and I still haven't received anything.",
    "Checkout has become really annoying lately.",
    "I keep getting an error at the last step.",
    "My order is taking forever.",
    "Still waiting for my stuff.",
    "It said it would arrive yesterday.",
    "Delivery is always late these days.",
    "I can't find my refund anywhere.",
    "They said my money was returned but I haven't got it.",
    "Why is this app so slow?",
    "The app keeps freezing randomly.",
    "It worked before but now it crashes.",
    "Nothing happens when I click the button.",
    "The discount isn't working.",
    "I entered the code but nothing changed.",
    "The offer looked good but I couldn't use it.",
    "Search is not giving me what I want.",
    "I searched for it several times and still couldn't find it.",
    "The results are completely off.",
    "Finding the right product is frustrating.",
    "I don't know what happened to my order.",
    "Everything feels unnecessarily complicated.",
    "Some things work and some things don't.",
    "Not happy with the experience.",
    "I expected this to be much easier.",
    "Please fix this.",
]

# ---------- AI ----------
def get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)

def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)

def analyze_with_ai(feedbacks):
    client = get_client()
    if not client:
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    schema = """
Return ONLY a JSON array. One object per feedback item with exactly:
sentiment, category, topic, product_area, severity, intent, summary, key_issue, evidence, confidence.
Rules:
- Do not invent facts.
- If something is unknown, use "Not provided".
- evidence must be a short phrase copied from the input.
- confidence must be a number from 0 to 1.
- severity must be Low, Medium, or High.
- sentiment must be Positive, Neutral, or Negative.
"""

    numbered = "\n".join(f"{i+1}. {x}" for i, x in enumerate(feedbacks))
    prompt = f"""You are a product analytics assistant. Analyze these customer feedback messages.
{schema}
FEEDBACK:
{numbered}
"""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )
        return extract_json(response.text)

    except Exception as e:
        # Keep the demo usable when Gemini is temporarily unavailable,
        # including free-tier quota (429) errors.
        error_text = str(e)
        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
            st.warning(
                "🟡 **Demo Mode active:** Gemini's current quota is temporarily "
                "unavailable. FeedbackIQ is using its local analysis engine so "
                "you can continue exploring the product."
            )
        else:
            st.warning(
                "🟡 **Demo Mode active:** AI analysis is temporarily unavailable. "
                "FeedbackIQ is using its local analysis engine."
            )
        return None

def demo_fallback(feedbacks):
    rows = []
    for text in feedbacks:
        low = text.lower()
        if any(x in low for x in ["pay", "payment", "charged", "money", "checkout"]):
            topic, category, area, sev = "Payment issues", "Payment", "Checkout", "High"
        elif any(x in low for x in ["delivery", "arrive", "waiting", "order"]):
            topic, category, area, sev = "Delivery / order issues", "Order", "Delivery", "Medium"
        elif any(x in low for x in ["refund", "returned", "money"]):
            topic, category, area, sev = "Refund issues", "Refund", "Payments", "Medium"
        elif any(x in low for x in ["slow", "freez", "crash"]):
            topic, category, area, sev = "App performance", "Technical", "App", "High"
        elif any(x in low for x in ["discount", "coupon", "offer"]):
            topic, category, area, sev = "Promotion issues", "Promotion", "Offers", "Medium"
        elif any(x in low for x in ["search", "find", "results"]):
            topic, category, area, sev = "Search experience", "Search", "Discovery", "Medium"
        else:
            topic, category, area, sev = "General experience", "Experience", "Product", "Low"

        sentiment = "Negative" if any(x in low for x in ["wrong", "doesn't", "failed", "late", "slow", "frustrat", "not ", "nothing", "crash", "annoying", "can't", "don't", "problem", "please fix"]) else "Neutral"
        rows.append({
            "sentiment": sentiment, "category": category, "topic": topic,
            "product_area": area, "severity": sev, "intent": "Complaint",
            "summary": text[:90], "key_issue": topic,
            "evidence": text, "confidence": 0.78
        })
    return rows

def make_analysis(feedbacks):
    ai_rows = analyze_with_ai(feedbacks)
    return ai_rows if ai_rows and len(ai_rows) == len(feedbacks) else demo_fallback(feedbacks)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 💡 FeedbackIQ")
    st.caption("AI Customer Feedback Intelligence")
    st.divider()

    st.markdown("### What you can do")
    st.markdown("""
    **📥 Upload** customer feedback  
    **🧠 Analyze** unstructured comments  
    **🔎 Discover** recurring problems  
    **📌 Prioritize** important themes  
    **💬 Validate** with customer evidence
    """)

    st.divider()
    st.markdown("### How it works")
    st.markdown("""
    **Feedback**  
    ↓  
    **AI language analysis**  
    ↓  
    **Recurring themes**  
    ↓  
    **Product insights**
    """)

    st.divider()
    st.caption("AI interprets language. Deterministic logic handles aggregation and prioritization.")
    st.caption("Prototype • Synthetic data")

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">AI PRODUCT ANALYTICS</div>
  <h1>FeedbackIQ</h1>
  <p>Turn messy customer feedback into clear product decisions.</p>
  <div class="flow">
    <span>💬 Feedback</span><b>→</b><span>🧠 AI Analysis</span><b>→</b><span>🔎 Themes</span><b>→</b><span>📌 Insights</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- Data controls ----------
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []
if "results" not in st.session_state:
    st.session_state.results = None
if "source" not in st.session_state:
    st.session_state.source = None

c1, c2 = st.columns([1, 2])
with c1:
    if st.button("🚀 Try Demo Dataset", use_container_width=True, type="primary"):
        st.session_state.feedbacks = DEMO_FEEDBACK
        st.session_state.source = "Demo dataset"
        st.session_state.results = None
        st.rerun()

with c2:
    uploaded = st.file_uploader(
        "📁 Upload CSV (must contain a 'feedback' column)",
        type=["csv"],
        label_visibility="visible",
    )

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        if "feedback" not in df.columns:
            st.error("Your CSV needs a column named `feedback`.")
        else:
            st.session_state.feedbacks = df["feedback"].dropna().astype(str).tolist()[:200]
            st.session_state.source = uploaded.name
            st.session_state.results = None
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

if st.session_state.feedbacks:
    st.success(f"Loaded **{len(st.session_state.feedbacks)}** feedback items from **{st.session_state.source}**.")

    with st.expander("👀 Preview customer feedback", expanded=False):
        st.dataframe(pd.DataFrame({"feedback": st.session_state.feedbacks}).head(10), use_container_width=True, hide_index=True)

    if st.button("✨ Analyze Feedback", use_container_width=True):
        with st.spinner("AI is interpreting customer language and finding patterns..."):
            st.session_state.results = make_analysis(st.session_state.feedbacks)

# ---------- Results ----------
results = st.session_state.results

if results:
    rdf = pd.DataFrame(results)
    rdf["severity"] = rdf["severity"].fillna("Medium")
    rdf["sentiment"] = rdf["sentiment"].fillna("Neutral")
    rdf["topic"] = rdf["topic"].fillna("Uncategorized")

    st.markdown("## 📊 Feedback Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">FEEDBACK ANALYZED</div><div class="metric-value">{len(rdf)}</div><div class="metric-sub">Customer comments processed</div></div>', unsafe_allow_html=True)
    with m2:
        neg = int((rdf["sentiment"].str.lower() == "negative").sum())
        st.markdown(f'<div class="metric-card"><div class="metric-label">NEGATIVE FEEDBACK</div><div class="metric-value">{neg}</div><div class="metric-sub">{neg/len(rdf):.0%} of analyzed feedback</div></div>', unsafe_allow_html=True)
    with m3:
        high = int((rdf["severity"].str.lower() == "high").sum())
        st.markdown(f'<div class="metric-card"><div class="metric-label">HIGH SEVERITY</div><div class="metric-value">{high}</div><div class="metric-sub">Potentially urgent issues</div></div>', unsafe_allow_html=True)
    with m4:
        themes = rdf["topic"].nunique()
        st.markdown(f'<div class="metric-card"><div class="metric-label">RECURRING THEMES</div><div class="metric-value">{themes}</div><div class="metric-sub">Distinct issue clusters</div></div>', unsafe_allow_html=True)

    # Use a custom navigation control instead of Streamlit tabs.
    # This avoids theme-dependent tab text colors and guarantees readability.
    if "active_view" not in st.session_state:
        st.session_state.active_view = "🎯 Overview"

    st.markdown("""
    <div class="nav-heading">Explore your feedback</div>
    """, unsafe_allow_html=True)

    selected = st.radio(
        "Dashboard section",
        ["🎯 Overview", "🔎 Themes", "💬 Customer Evidence", "🤖 AI Insight"],
        index=["🎯 Overview", "🔎 Themes", "💬 Customer Evidence", "🤖 AI Insight"].index(st.session_state.active_view),
        horizontal=True,
        label_visibility="collapsed",
        key="feedback_navigation",
    )
    st.session_state.active_view = selected

    if selected == "🎯 Overview":
        left, right = st.columns(2)

        def clean_bar_chart(series, title, subtitle):
            chart_df = series.rename("Count").reset_index()
            chart_df.columns = ["Category", "Count"]
            fig = px.bar(
                chart_df,
                x="Category",
                y="Count",
                text="Count",
                title=title,
            )
            fig.update_traces(
                marker_color="#2563eb",
                marker_line_width=0,
                textposition="outside",
            )
            fig.update_layout(
                title_font_size=16,
                title_font_color="#0f172a",
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#334155", family="Arial"),
                margin=dict(l=10, r=10, t=55, b=15),
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    zeroline=False,
                    tickfont=dict(color="#475569"),
                ),
                yaxis=dict(
                    title=None,
                    showgrid=True,
                    gridcolor="#e5e7eb",
                    zeroline=False,
                    tickfont=dict(color="#64748b"),
                ),
                hoverlabel=dict(
                    bgcolor="#0f172a",
                    font_color="#ffffff",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(subtitle)

        with left:
            sent = rdf["sentiment"].value_counts()
            clean_bar_chart(sent, "Sentiment", "How customers feel about the product")

        with right:
            sev = rdf["severity"].value_counts()
            clean_bar_chart(sev, "Severity", "Potential urgency of identified issues")

        st.markdown("### Top recurring issues")
        topics = rdf["topic"].value_counts().head(8)
        clean_bar_chart(topics, "Recurring customer problems", "Most frequently detected issue areas")

    elif selected == "🔎 Themes":
        topic_counts = rdf["topic"].value_counts()
        for topic, count in topic_counts.head(10).items():
            subset = rdf[rdf["topic"] == topic]
            severity = Counter(subset["severity"]).most_common(1)[0][0]
            st.markdown(f"""
            <div class="theme-card">
              <strong>{topic}</strong>
              <span class="pill">{count} mentions</span>
              <span class="pill">{severity} severity</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Prioritization logic")
        st.info("Priority is intentionally transparent: recurring frequency + severity. In a production version, business impact, affected users and trend velocity could be added.")

    elif selected == "💬 Customer Evidence":
        st.markdown("### Evidence behind the AI")
        st.caption("The original customer statements remain visible so a PM can validate the generated insight.")
        for i, row in rdf.iterrows():
            with st.expander(f"{i+1}. {row.get('topic', 'Issue')} · {row.get('severity', 'Medium')}"):
                st.write(f"**Customer feedback:** {st.session_state.feedbacks[i]}")
                st.write(f"**AI summary:** {row.get('summary', 'Not provided')}")
                st.write(f"**Key issue:** {row.get('key_issue', 'Not provided')}")
                st.write(f"**Confidence:** {float(row.get('confidence', 0)):.0%}")

    elif selected == "🤖 AI Insight":
        top_topic = rdf["topic"].value_counts().index[0]
        top_count = int(rdf["topic"].value_counts().iloc[0])
        high_topics = rdf[rdf["severity"].str.lower() == "high"]["topic"].value_counts()

        st.markdown("### 💡 Product insight")
        st.markdown(f"""
        <div class="insight">
        <strong>Recurring issue detected: {top_topic}</strong><br><br>
        This theme appears <strong>{top_count} times</strong> in the analyzed feedback.
        The next step for a product team would be to validate the underlying customer
        evidence, quantify business impact, and investigate the relevant product workflow.
        </div>
        """, unsafe_allow_html=True)

        if len(high_topics):
            st.markdown("### ⚠️ High-severity signals")
            st.write(", ".join([f"{k} ({v})" for k, v in high_topics.head(5).items()]))

        st.markdown("### 🧭 Recommended PM workflow")
        st.markdown("""
        1. **Validate** the theme using customer evidence.
        2. **Quantify** affected users and business impact.
        3. **Investigate** the product/process root cause.
        4. **Prioritize** against other product opportunities.
        5. **Measure** whether the intervention reduces the recurring issue.
        """)

    st.divider()
    st.caption("FeedbackIQ is a portfolio prototype using synthetic customer feedback. AI-generated classifications should be validated before product decisions.")
else:
    st.markdown("## 👋 Start exploring")
    a, b, c = st.columns(3)
    with a:
        st.markdown("### 1. 📥 Bring feedback")
        st.write("Upload a CSV or use the built-in demo dataset.")
    with b:
        st.markdown("### 2. 🧠 Analyze")
        st.write("AI extracts topics, sentiment, severity and the underlying issue.")
    with c:
        st.markdown("### 3. 📌 Decide")
        st.write("Explore recurring themes and validate them using customer evidence.")

    st.info("Tip: Click **Try Demo Dataset** above to see the complete experience instantly.")
