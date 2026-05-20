"""
app.py — AI Code Review Agent
==============================
Paste any code → AI reviews it like a senior engineer
Finds: bugs, security issues, performance problems, style issues
Gives: line-by-line fixes, severity levels, overall grade A-F
Uses: Groq API (free) with LLaMA 3.3 70B
"""

import streamlit as st
from groq import Groq
import json
import re

# Basic Page Setup 
st.set_page_config(
    page_title="CodeSentinel · AI Code Review",
    page_icon="🛡️",
    layout="wide"
)

# CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg:         #0d1117;
    --bg2:        #161b22;
    --bg3:        #1c2128;
    --border:     #30363d;
    --text:       #e6edf3;
    --text2:      #8b949e;
    --critical:   #ff7b72;
    --warning:    #e3b341;
    --suggestion: #58a6ff;
    --positive:   #3fb950;
    --accent:     #f78166;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }

div[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}

/* Header */
.header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 20px;
    margin-bottom: 28px;
}
.header-title {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: var(--text);
}
.header-title span { color: var(--accent); }
.header-sub {
    font-size: 0.85rem;
    color: var(--text2);
    margin-top: 4px;
    font-family: 'IBM Plex Mono', monospace;
}

/* Grade card */
.grade-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 24px;
    text-align: center;
    margin-bottom: 20px;
}
.grade-letter {
    font-size: 4rem;
    font-weight: 700;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1;
}
.grade-A { color: var(--positive); }
.grade-B { color: #58a6ff; }
.grade-C { color: var(--warning); }
.grade-D { color: var(--critical); }
.grade-F { color: #ff4444; }
.grade-label {
    font-size: 0.75rem;
    color: var(--text2);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 6px;
    font-family: 'IBM Plex Mono', monospace;
}
.grade-explanation {
    font-size: 0.85rem;
    color: var(--text2);
    margin-top: 10px;
    line-height: 1.5;
}

/* Score row */
.score-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}
.score-box {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}
.score-num  { font-size: 1.8rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.score-lbl  { font-size: 0.68rem; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* Issue card */
.issue {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.issue.critical   { border-left: 3px solid var(--critical); }
.issue.warning    { border-left: 3px solid var(--warning); }
.issue.suggestion { border-left: 3px solid var(--suggestion); }
.issue.positive   { border-left: 3px solid var(--positive); }

.issue-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    flex-wrap: wrap;
}
.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}
.badge-critical   { background: #3d1a1a; color: var(--critical);   border: 1px solid #ff7b7230; }
.badge-warning    { background: #2d2208; color: var(--warning);    border: 1px solid #e3b34130; }
.badge-suggestion { background: #0d1f2d; color: var(--suggestion); border: 1px solid #58a6ff30; }
.badge-positive   { background: #0d2016; color: var(--positive);   border: 1px solid #3fb95030; }
.badge-cat        { background: var(--bg3); color: var(--text2); border: 1px solid var(--border); }

.issue-title { font-weight: 600; font-size: 0.92rem; flex: 1; }
.issue-line  {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text2);
    background: var(--bg3);
    padding: 2px 8px;
    border-radius: 4px;
}
.issue-desc { font-size: 0.87rem; color: var(--text2); line-height: 1.55; margin-bottom: 10px; }
.fix-label  { font-size: 0.7rem; color: var(--positive); font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
.fix-code {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #a5d6ff;
    white-space: pre-wrap;
    overflow-x: auto;
    line-height: 1.5;
}
.fix-explain { font-size: 0.82rem; color: var(--text2); margin-top: 8px; font-style: italic; }

/* Top tip */
.tip-box {
    background: #0a1628;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #7eb8f7;
    margin-top: 16px;
}

/* Buttons */
.stButton > button {
    background: #238636 !important;
    color: white !important;
    border: 1px solid #2ea043 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 10px !important;
}
.stButton > button:hover { background: #2ea043 !important; }

textarea { font-family: 'IBM Plex Mono', monospace !important; font-size: 0.82rem !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { color: var(--text2) !important; font-family: 'IBM Plex Sans', sans-serif !important; }
.stTabs [aria-selected="true"] { color: var(--text) !important; border-bottom: 2px solid var(--accent) !important; }

.stSelectbox > div > div { background: var(--bg2) !important; border: 1px solid var(--border) !important; color: var(--text) !important; }

.footer { text-align: center; color: var(--text2); font-size: 0.72rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--border); font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# Some Sample code snippets
SAMPLES = {
    "Python — SQL Injection Bug": '''def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = \'{username}\'"
    cursor.execute(query)
    return cursor.fetchone()

def login(username, password):
    user = get_user(username)
    if user and user[2] == password:
        return {"status": "ok", "user": user}
    return {"status": "fail"}
''',
    "Python — Memory Leak + N+1 Query": '''def process_orders(order_ids):
    results = []
    for order_id in order_ids:
        order = db.query(f"SELECT * FROM orders WHERE id={order_id}")
        user  = db.query(f"SELECT * FROM users WHERE id={order['user_id']}")
        items = db.query(f"SELECT * FROM items WHERE order_id={order_id}")
        large_data = [x * 2 for x in range(1000000)]
        results.append({"order": order, "user": user, "items": items})
    return results
''',
    "JavaScript — XSS + Async Bug": '''async function loadUserProfile(userId) {
    const response = await fetch(`/api/users/${userId}`)
    const user = response.json()
    document.getElementById('bio').innerHTML = user.bio
    const posts = await fetch(`/api/posts?user=${userId}`)
    return { name: user.name, posts: posts.json() }
}

function searchUsers(query) {
    document.getElementById('results').innerHTML = `Results for: ${query}`
}
''',
    "Paste your own code": ""
}


# Helper: extract JSON from LLM output 
# Groq sometimes returns json wrapped in extra text so this strips it out
def extract_json(text: str) -> str:
    """Pull JSON out of LLM response even if it has extra text around it."""
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    start = -1
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start == -1:
        return text
    open_char  = text[start]
    close_char = "}" if open_char == "{" else "]"
    depth = 0
    for i in range(start, len(text)):
        if text[i] == open_char:
            depth += 1
        elif text[i] == close_char:
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return text[start:]


# Sending code to groq and gets back the review
# this is the main function that sends code to the AI and gets back the review
# i prompt it to return json so i can display each issue separately
def review_code(code: str, language: str, api_key: str) -> dict:
    """
    Send code to LLaMA via Groq and get back a structured review.
    Returns a dict with grade, issues, positives, top_tip.
    """
    client = Groq(api_key=api_key)

    prompt = f"""You are a senior software engineer doing a thorough code review.

Review this {language} code and find ALL real issues:

```{language}
{code}
```

Return ONLY valid JSON, no markdown, no explanation:
{{
  "overall_grade": "A|B|C|D|F",
  "grade_explanation": "2 sentence explanation of the grade",
  "issues": [
    {{
      "severity": "critical|warning|suggestion|positive",
      "category": "security|bug|performance|style|logic|best-practice",
      "title": "Short title",
      "line_range": "e.g. Line 3-5",
      "description": "Why this is a problem and its impact",
      "fixed_code": "The corrected code snippet",
      "explanation": "Why the fix works"
    }}
  ],
  "positive_aspects": ["thing done well 1", "thing done well 2"],
  "top_tip": "Single most important thing to fix first"
}}

Rules:
- Find REAL issues only, not imaginary ones
- fixed_code must be actual working code
- severity=positive is for things done well
- Be specific about line numbers"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": "You are a senior code reviewer. Respond with ONLY valid JSON. No text before or after."},
            {"role": "user",   "content": prompt}
        ]
    )

    raw    = extract_json(resp.choices[0].message.content)
    result = json.loads(raw)
    return result


# Store the result so it doesnt disappear when streamlit reruns
if "result" not in st.session_state:
    st.session_state.result = None


# Sidebar - api key, language picker, sample selector
with st.sidebar:
    st.markdown("### ⚙️ Config")
    api_key  = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    language = st.selectbox("Language", ["Python", "JavaScript", "TypeScript", "Java", "Go", "SQL", "Other"])

    st.markdown("---")
    st.markdown("### 📋 Load Sample")
    sample = st.selectbox("Pick a sample", list(SAMPLES.keys()))

    st.markdown("---")
    st.markdown("**What it checks:**")
    st.markdown("🔴 Critical bugs\n\n🟡 Warnings\n\n🔵 Suggestions\n\n✅ Positives")

    if st.session_state.result:
        st.markdown("---")
        issues   = st.session_state.result.get("issues", [])
        critical = sum(1 for i in issues if i["severity"] == "critical")
        warnings = sum(1 for i in issues if i["severity"] == "warning")
        st.markdown("**Last review:**")
        st.markdown(f"Grade: **{st.session_state.result.get('overall_grade', '?')}**")
        st.markdown(f"Critical: **{critical}**")
        st.markdown(f"Warnings: **{warnings}**")


# App Header 
st.markdown("""
<div class="header">
    <div class="header-title">🛡️ Code<span>Sentinel</span></div>
    <div class="header-sub">AI code review agent · finds bugs before production does</div>
</div>
""", unsafe_allow_html=True)


# Load the selected sample into the text area by default
default_code = SAMPLES.get(sample, "") if sample != "Paste your own code" else ""

code_input = st.text_area(
    "PASTE YOUR CODE",
    value=default_code,
    height=300,
    placeholder="Paste any code here — Python, JavaScript, SQL, Java, Go..."
)

# Disable the button if no api key
review_btn = st.button("🚀 Review My Code", disabled=not api_key)


# Run review:    send code to groq and save result
if review_btn and code_input.strip():
    if not api_key:
        st.error("Add your Groq API key in the sidebar.")
    else:
        with st.spinner("🤖 Reviewing your code..."):
            try:
                result = review_code(code_input, language, api_key)
                st.session_state.result = result
                st.rerun()
            except json.JSONDecodeError:
                st.error("Could not parse response. Try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# Display results 
if st.session_state.result:
    result   = st.session_state.result
    issues   = result.get("issues", [])
    grade    = result.get("overall_grade", "?")

    # Count by severity
    critical_c   = sum(1 for i in issues if i["severity"] == "critical")
    warning_c    = sum(1 for i in issues if i["severity"] == "warning")
    suggestion_c = sum(1 for i in issues if i["severity"] == "suggestion")
    positive_c   = sum(1 for i in issues if i["severity"] == "positive")

    # Grade + score row 
    col1, col2 = st.columns([1, 2])

    with col1:
        grade_class = f"grade-{grade[0] if grade else 'B'}"
        st.markdown(f"""
<div class="grade-card">
    <div class="grade-letter {grade_class}">{grade}</div>
    <div class="grade-label">Overall Grade</div>
    <div class="grade-explanation">{result.get('grade_explanation', '')}</div>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div class="score-row">
    <div class="score-box">
        <div class="score-num" style="color:#ff7b72;">{critical_c}</div>
        <div class="score-lbl">Critical</div>
    </div>
    <div class="score-box">
        <div class="score-num" style="color:#e3b341;">{warning_c}</div>
        <div class="score-lbl">Warnings</div>
    </div>
    <div class="score-box">
        <div class="score-num" style="color:#58a6ff;">{suggestion_c}</div>
        <div class="score-lbl">Suggestions</div>
    </div>
    <div class="score-box">
        <div class="score-num" style="color:#3fb950;">{positive_c}</div>
        <div class="score-lbl">Positives</div>
    </div>
</div>
""", unsafe_allow_html=True)

        # Top tip
        if result.get("top_tip"):
            st.markdown(f'<div class="tip-box">💡 <strong>Top fix:</strong> {result["top_tip"]}</div>',
                       unsafe_allow_html=True)

    st.markdown("---")

    # Issues list : issues and positives
    tab1, tab2 = st.tabs(["📋 All Issues", "✅ Positives"])

    with tab1:
        # Sort: critical first, then warning, suggestion, positive
        order   = {"critical": 0, "warning": 1, "suggestion": 2, "positive": 3}
        sorted_issues = sorted(issues, key=lambda x: order.get(x.get("severity", "suggestion"), 99))

        non_positive = [i for i in sorted_issues if i.get("severity") != "positive"]

        if non_positive:
            for issue in non_positive:
                sev  = issue.get("severity", "suggestion")
                cat  = issue.get("category", "")
                icon = {"critical": "🔴", "warning": "🟡", "suggestion": "🔵"}.get(sev, "•")

                # Escape HTML in code to prevent rendering issues
                fixed_code = issue.get("fixed_code", "").replace("<", "&lt;").replace(">", "&gt;")

                st.markdown(f"""
<div class="issue {sev}">
    <div class="issue-header">
        <span class="badge badge-{sev}">{icon} {sev}</span>
        <span class="badge badge-cat">{cat}</span>
        <span class="issue-title">{issue.get('title','')}</span>
        <span class="issue-line">{issue.get('line_range','')}</span>
    </div>
    <div class="issue-desc">{issue.get('description','')}</div>
    <div class="fix-label">✦ Suggested fix</div>
    <div class="fix-code">{fixed_code}</div>
    <div class="fix-explain">{issue.get('explanation','')}</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#3fb950; padding:20px; text-align:center;">✅ No issues found — great code!</div>',
                       unsafe_allow_html=True)

    with tab2:
        positives = result.get("positive_aspects", [])
        if positives:
            for p in positives:
                st.markdown(f'<div style="color:#3fb950; padding:8px 0; border-bottom:1px solid #21262d; font-size:0.9rem;">✓ {p}</div>',
                           unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#8b949e; padding:20px; text-align:center;">No specific positives noted.</div>',
                       unsafe_allow_html=True)

# Shown when no review has been run yet
else:
    st.markdown("""
<div style="text-align:center; padding:60px 20px; color:#8b949e;">
    <div style="font-size:3rem; margin-bottom:16px;">🛡️</div>
    <div style="font-size:1.1rem; font-weight:600; margin-bottom:8px; color:#e6edf3;">Paste your code and click Review</div>
    <div style="font-size:0.85rem;">Finds bugs, security issues, performance problems — with working fixes</div>
    <div style="margin-top:16px; font-size:0.82rem;">← Try a sample from the sidebar to see it in action</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">CodeSentinel · Python · Groq API · LLaMA 3.3 70B · Streamlit</div>',
           unsafe_allow_html=True)
