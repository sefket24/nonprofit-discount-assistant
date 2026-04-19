# 🤝 AI Nonprofit Discount Assistant

> AI-powered eligibility screening for SaaS support teams — built with Python, Streamlit, and OpenAI.

## Live Demo

Try the working prototype here:
https://nonprofit-discount-assistant.streamlit.app/

---

## Overview

The **AI Nonprofit Discount Assistant** is a minimal MVP web app that simulates a SaaS support workflow for processing nonprofit discount requests. It uses a large language model to evaluate applicant messages, classify eligibility, and draft a suggested support response — all in real time.

---

## Problem

Support teams at SaaS companies frequently receive nonprofit discount requests through their help portals. These requests vary wildly in quality, completeness, and legitimacy. Manually reviewing each one is:

- Time-consuming for support agents
- Inconsistent across team members
- Hard to scale as request volume grows

---

## Solution

This tool provides an AI-powered first-pass review. An agent fills out the request form (or pastes an incoming ticket), and the assistant instantly returns:

- A **classification** (Eligible / Needs Review / Not Eligible)
- A **reasoning summary**
- A **tone analysis** of the request
- A **suggested reply** ready to copy and send
- **Tags** for categorization and tracking

This frees support agents to focus on edge cases, exceptions, and relationship-building — not repetitive triage.

---

## How It Works

1. The support agent (or applicant) fills in the request form:
   - Organization name
   - Contact email
   - Free-text description of their mission and discount request
   - Checkbox confirming proof of nonprofit status

2. On submission, a structured prompt is sent to the OpenAI API (`gpt-4o-mini`).

3. The model returns a JSON object with classification, reasoning, tone, suggested response, and tags.

4. Results are displayed in a clean side-by-side layout with color-coded status badges.

---

## Example Input / Output

**Input:**
- Org: `Bright Futures Youth Mentorship`
- Email: `grants@brightfutures.org`
- Message: *"We are a registered 501(c)(3) supporting underserved youth in rural areas. We'd love to explore your platform for case management — a discount would help us stretch our grant funding."*
- Proof provided: ✅ Yes

**Output:**
```json
{
  "classification": "eligible",
  "reasoning": "The organization is a registered 501(c)(3) with a clear charitable mission serving underserved youth. Proof of status was provided and the use case is mission-aligned.",
  "tone": "Professional and mission-driven",
  "suggested_response": "Thank you for reaching out, Bright Futures Youth Mentorship! We're delighted to support your work with underserved youth. Based on your 501(c)(3) status, you qualify for our nonprofit discount. Please reply to this ticket with your EIN and a team member will apply the discount within 1 business day.",
  "tags": ["verified-nonprofit", "youth-services", "501c3", "eligible"]
}
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/nonprofit-discount-assistant.git
cd nonprofit-discount-assistant
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder with your real key:

```
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - AI Nonprofit Discount Assistant"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nonprofit-discount-assistant.git
git push -u origin main
```

> **Note:** When prompted for a password, use your GitHub Personal Access Token — not your account password.

---

## Deploy on Streamlit Cloud

1. Push your repo to GitHub (see above)
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New app** → connect your GitHub account
4. Select your repo and set `app.py` as the main file
5. Under **Advanced settings → Secrets**, add:

```
OPENAI_API_KEY = "sk-...your-key-here..."
```

6. Click **Deploy** — your app will be live in seconds

---

## Tech Stack

| Layer | Tool |
|-------|------|
| UI | Streamlit |
| AI | OpenAI GPT-4o-mini |
| Config | python-dotenv |
| Language | Python 3.10+ |

---

## Inspiration

This project was inspired by real-world SaaS support workflows — specifically the challenge of processing high volumes of nonprofit discount requests consistently and efficiently. It demonstrates how a focused AI integration can meaningfully reduce manual review time while improving response quality.

---

## License

MIT — free to use, modify, and build on.
