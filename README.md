# 🛡️ CodeSentinel — AI Code Review Agent

> Paste any code — Python, JavaScript, SQL, Java, Go. Get an instant AI review like a senior engineer: bugs found, security issues flagged, performance problems identified, with working line-by-line fixes.

## 📸 Screenshots
*(add screenshots here)*

---

## ✨ Features

- **Overall grade A–F** with explanation
- **4 severity levels** — Critical 🔴, Warning 🟡, Suggestion 🔵, Positive ✅
- **6 issue categories** — security, bug, performance, style, logic, best-practice
- **Working fixes** — actual corrected code, not vague advice
- **Line-by-line** — tells you exactly where each issue is
- **Top tip** — the single most important thing to fix first
- **3 built-in samples** — SQL injection, memory leak, XSS vulnerability pre-loaded

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Groq API (LLaMA 3.3 70B) | AI code analysis — free |
| Streamlit | Web UI |

---

## 📦 Setup & Run

```bash
git clone https://github.com/YOUR_USERNAME/codesentinel
cd codesentinel
pip install -r requirements.txt
streamlit run app.py
```

Get a free API key at [console.groq.com](https://console.groq.com)

---

## 🧪 Sample Issues It Catches

| Sample | Issues Found |
|---|---|
| SQL user lookup | SQL injection (critical), plaintext password comparison (critical) |
| Order processor | N+1 query problem (warning), memory leak (warning) |
| JS profile loader | Missing await bug (critical), XSS vulnerability (critical) |

---

## 🧠 What I Learned

- How to design effective prompts for structured JSON output from LLMs
- Parsing and validating LLM responses reliably
- Classifying code issues by severity and category
- Building clean developer tools with Streamlit

---

## 📈 Future Improvements

- [ ] File upload support (.py, .js, .ts)
- [ ] GitHub PR integration
- [ ] Compare before/after code side by side
- [ ] Export review as PDF report

---

## 📄 License
MIT
