import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nonprofit Discount Assistant",
    page_icon="🤝",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: #f7f6f2;
    }

    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: -0.5px;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 1100px;
    }

    /* Header strip */
    .app-header {
        background: #111111;
        color: #f7f6f2;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header h1 {
        color: #f7f6f2;
        margin: 0;
        font-size: 1.4rem;
        font-weight: 600;
    }
    .app-header p {
        margin: 0;
        font-size: 0.85rem;
        color: #888;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 300;
    }
    .badge {
        background: #c8f55a;
        color: #111;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* Form card */
    .form-card {
        background: #ffffff;
        border: 1px solid #e0ddd6;
        border-radius: 12px;
        padding: 1.75rem;
    }

    /* Result card */
    .result-card {
        background: #ffffff;
        border: 1px solid #e0ddd6;
        border-radius: 12px;
        padding: 1.75rem;
        height: 100%;
    }

    .result-placeholder {
        background: #f7f6f2;
        border: 2px dashed #d4d0c8;
        border-radius: 8px;
        padding: 3rem 2rem;
        text-align: center;
        color: #aaa;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
    }

    /* Status badges */
    .status-eligible {
        display: inline-block;
        background: #d4f7d4;
        color: #1a6b1a;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 6px;
        border: 1px solid #a8e6a8;
        margin-bottom: 1rem;
    }
    .status-needs-review {
        display: inline-block;
        background: #fff7d4;
        color: #7a5c00;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 6px;
        border: 1px solid #f0d890;
        margin-bottom: 1rem;
    }
    .status-not-eligible {
        display: inline-block;
        background: #fde8e8;
        color: #8b1a1a;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 6px;
        border: 1px solid #f0a8a8;
        margin-bottom: 1rem;
    }

    /* Suggested response box */
    .response-box {
        background: #f7f6f2;
        border-left: 4px solid #111111;
        border-radius: 0 8px 8px 0;
        padding: 1.25rem 1.5rem;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #333;
        margin-top: 0.5rem;
        white-space: pre-wrap;
    }

    /* Tags */
    .tag {
        display: inline-block;
        background: #111111;
        color: #f7f6f2;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        padding: 3px 10px;
        border-radius: 4px;
        margin: 3px 3px 3px 0;
    }

    /* Section label */
    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.35rem;
        margin-top: 1.1rem;
    }

    /* Streamlit overrides */
    .stButton > button {
        background: #111111;
        color: #f7f6f2;
        border: none;
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        width: 100%;
        letter-spacing: 0.5px;
        transition: background 0.15s;
    }
    .stButton > button:hover {
        background: #333;
        color: #c8f55a;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #d4d0c8;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.9rem;
        background: #fafaf8;
    }

    .stCheckbox > label {
        font-size: 0.9rem;
        color: #444;
    }

    div[data-testid="stVerticalBlock"] > div:has(.form-card) {
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <h1>🤝 Nonprofit Discount Assistant</h1>
        <p>AI-powered eligibility screening for SaaS support teams</p>
    </div>
    <div class="badge">AI-Powered</div>
</div>
""", unsafe_allow_html=True)


# ── AI Function ───────────────────────────────────────────────────────────────
def analyze_request(org_name: str, email: str, message: str, has_proof: bool) -> dict:
    """Call OpenAI and return structured eligibility analysis."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        st.error("⚠️  OPENAI_API_KEY not found. Add it to your .env file.")
        st.stop()

    client = OpenAI(api_key=api_key)

    proof_note = "The organization HAS provided proof of nonprofit status." if has_proof else \
                 "The organization has NOT provided proof of nonprofit status."

    prompt = f"""You are a SaaS support agent reviewing a nonprofit discount request.

Organization: {org_name}
Email: {email}
Proof of nonprofit status provided: {has_proof}
Note: {proof_note}

Request message:
\"\"\"{message}\"\"\"

Analyze this request and return ONLY a valid JSON object (no markdown, no explanation) with these fields:
{{
  "classification": "eligible" | "needs_more_info" | "not_eligible",
  "reasoning": "2-3 sentence explanation of why this classification was chosen",
  "tone": "Brief description of the request's tone (e.g. professional, informal, urgent)",
  "suggested_response": "A warm, professional support team reply to send to the applicant (3-5 sentences)",
  "tags": ["tag1", "tag2", "tag3"]  // 2-4 relevant tags like: verified-nonprofit, missing-docs, educational, healthcare, etc.
}}

Classification rules:
- eligible: Has proof AND message clearly describes nonprofit/charitable mission
- needs_more_info: No proof provided OR mission is unclear OR details are missing
- not_eligible: Message suggests commercial intent, for-profit operation, or is clearly ineligible
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


# ── Layout ────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown("#### Submit a Discount Request")
    st.markdown("---")

    org_name = st.text_input("Organization Name", placeholder="e.g. Green Earth Foundation")
    email    = st.text_input("Contact Email", placeholder="e.g. hello@greenearth.org")
    message  = st.text_area(
        "Request Message",
        placeholder="Describe your organization, its mission, and why you're requesting a nonprofit discount...",
        height=180,
    )
    has_proof = st.checkbox("✅ We have uploaded proof of nonprofit status (501c3 or equivalent)")

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("🔍 Analyze Eligibility")
    st.markdown('</div>', unsafe_allow_html=True)


with right_col:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("#### Eligibility Analysis")
    st.markdown("---")

    if not submit:
        st.markdown("""
        <div class="result-placeholder">
            Submit a request on the left<br>to see the AI analysis here.
        </div>
        """, unsafe_allow_html=True)

    else:
        # Validation
        if not org_name.strip() or not message.strip():
            st.warning("Please fill in the Organization Name and Request Message.")
        else:
            with st.spinner("Analyzing request..."):
                try:
                    result = analyze_request(org_name, email, message, has_proof)
                except json.JSONDecodeError:
                    st.error("The AI returned an unexpected format. Please try again.")
                    st.stop()
                except Exception as e:
                    st.error(f"API error: {e}")
                    st.stop()

            # ── Status badge ──
            classification = result.get("classification", "needs_more_info")
            if classification == "eligible":
                st.markdown('<span class="status-eligible">✅ Eligible</span>', unsafe_allow_html=True)
            elif classification == "not_eligible":
                st.markdown('<span class="status-not-eligible">❌ Not Eligible</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-needs-review">⚠️ Needs Review</span>', unsafe_allow_html=True)

            # ── Reasoning ──
            st.markdown('<div class="section-label">Reasoning</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.9rem;color:#333;line-height:1.6'>{result.get('reasoning','')}</p>", unsafe_allow_html=True)

            # ── Tone ──
            st.markdown('<div class="section-label">Request Tone</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.9rem;color:#555;font-style:italic'>{result.get('tone','')}</p>", unsafe_allow_html=True)

            # ── Suggested Response ──
            st.markdown('<div class="section-label">Suggested Response</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="response-box">{result.get("suggested_response","")}</div>',
                unsafe_allow_html=True,
            )

            # ── Tags ──
            tags = result.get("tags", [])
            if tags:
                st.markdown('<div class="section-label">Tags</div>', unsafe_allow_html=True)
                tag_html = " ".join(f'<span class="tag">{t}</span>' for t in tags)
                st.markdown(tag_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-size:0.75rem;color:#aaa;font-family:IBM Plex Mono,monospace'>"
    "AI Nonprofit Discount Assistant · Built with Streamlit + OpenAI"
    "</p>",
    unsafe_allow_html=True,
)
