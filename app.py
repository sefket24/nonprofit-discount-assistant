import streamlit as st
import json
import os
import base64
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nonprofit Discount Assistant",
    page_icon="🤝",
    layout="wide",
)

# ── Session state for stats ───────────────────────────────────────────────────
if "total_requests" not in st.session_state:
    st.session_state.total_requests = 0
if "eligible_count" not in st.session_state:
    st.session_state.eligible_count = 0
if "last_process_time" not in st.session_state:
    st.session_state.last_process_time = None

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .stApp { background-color: #f4f3ef; }
    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1140px;
    }

    /* ── Portfolio banner ── */
    .portfolio-banner {
        background: #fffdf0;
        border: 1px solid #f0e68c;
        border-left: 4px solid #c8f55a;
        border-radius: 8px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.25rem;
        font-size: 0.85rem;
        color: #444;
        line-height: 1.6;
    }
    .portfolio-banner strong { color: #111; font-weight: 600; }
    .portfolio-banner a {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: #333;
        text-decoration: none;
        border: 1px solid #d4d0c8;
        background: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 6px;
        white-space: nowrap;
    }

    /* ── Doc result ── */
    .doc-verified   { background:#d4f7d4; border:1px solid #a8e6a8; border-radius:8px; padding:0.6rem 1rem; font-size:0.82rem; color:#1a6b1a; font-family:'IBM Plex Mono',monospace; margin-bottom:1rem; }
    .doc-unverified { background:#fff7d4; border:1px solid #f0d890; border-radius:8px; padding:0.6rem 1rem; font-size:0.82rem; color:#7a5c00; font-family:'IBM Plex Mono',monospace; margin-bottom:1rem; }

    /* ── Status badges ── */
    .status-eligible    { display:inline-block; background:#d4f7d4; color:#1a6b1a; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600; padding:6px 14px; border-radius:6px; border:1px solid #a8e6a8; }
    .status-needs-review{ display:inline-block; background:#fff7d4; color:#7a5c00; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600; padding:6px 14px; border-radius:6px; border:1px solid #f0d890; }
    .status-not-eligible{ display:inline-block; background:#fde8e8; color:#8b1a1a; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600; padding:6px 14px; border-radius:6px; border:1px solid #f0a8a8; }

    /* ── Confidence bar ── */
    .confidence-wrap { margin: 0.75rem 0 1rem; }
    .confidence-label { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#888; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem; }
    .confidence-track { background:#f0efe9; border-radius:99px; height:8px; width:100%; overflow:hidden; }
    .confidence-fill  { height:100%; border-radius:99px; }
    .conf-high   { background:#4caf50; }
    .conf-medium { background:#ff9800; }
    .conf-low    { background:#f44336; }
    .confidence-pct { font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#555; margin-top:0.25rem; }

    /* ── Risk flags ── */
    .risk-flag {
        display:inline-block; background:#fff3e0; color:#e65100;
        border:1px solid #ffcc80; font-family:'IBM Plex Mono',monospace;
        font-size:0.7rem; padding:3px 9px; border-radius:4px; margin:2px 3px 2px 0;
    }

    /* ── Section label ── */
    .section-label {
        font-family:'IBM Plex Mono',monospace; font-size:0.68rem; font-weight:600; color:#999;
        text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem; margin-top:1rem;
    }

    /* ── Response box ── */
    .response-box {
        background:#f4f3ef; border-left:4px solid #111; border-radius:0 8px 8px 0;
        padding:1.1rem 1.4rem; font-size:0.88rem; line-height:1.75;
        color:#333; white-space:pre-wrap;
    }

    /* ── Tags ── */
    .tag { display:inline-block; background:#111; color:#f4f3ef; font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:3px 9px; border-radius:4px; margin:2px 3px 2px 0; }

    /* ── Process time ── */
    .process-time { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#bbb; text-align:right; margin-top:1rem; }

    /* ── Placeholder ── */
    .result-placeholder {
        background:#f4f3ef; border:2px dashed #d4d0c8; border-radius:8px;
        padding:3rem 2rem; text-align:center; color:#bbb;
        font-family:'IBM Plex Mono',monospace; font-size:0.82rem;
    }

    /* ── Streamlit overrides ── */
    .stButton > button {
        background:#111; color:#f4f3ef; border:none; border-radius:8px;
        font-family:'IBM Plex Mono',monospace; font-size:0.85rem; font-weight:600;
        padding:0.6rem 1.5rem; width:100%; letter-spacing:0.5px; transition:all 0.15s;
    }
    .stButton > button:hover { background:#333; color:#c8f55a; }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius:8px; border:1px solid #d4d0c8;
        font-family:'IBM Plex Sans',sans-serif; font-size:0.9rem; background:#fafaf8;
    }
    .stCheckbox > label { font-size:0.88rem; color:#444; }

    div[data-testid="stFileUploader"] {
        border:2px dashed #d4d0c8 !important;
        border-radius:8px !important;
        background:#fafaf8 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Header — native Streamlit (mobile safe) ───────────────────────────────────
st.markdown("## 🤝 Nonprofit Discount Assistant")
st.caption("AI-powered eligibility screening for SaaS support teams · Internal Tool")
st.divider()

# ── Portfolio banner ──────────────────────────────────────────────────────────
st.markdown("""
<div class="portfolio-banner">
    👋 <strong>Hey, hiring team!</strong> This is a portfolio project by <strong>Sef Nouri</strong> —
    a working AI app that simulates how SaaS support teams could automate nonprofit discount request triage
    using document verification and LLM-based eligibility classification. Feel free to test it with a real request.
    <br><br>
    <a href="https://github.com/sefket24/nonprofit-discount-assistant" target="_blank">⌥ GitHub</a>
    <a href="https://www.linkedin.com/in/sefketnouri/" target="_blank">in LinkedIn</a>
</div>
""", unsafe_allow_html=True)

# ── Stats row — native Streamlit columns (mobile safe) ───────────────────────
total    = st.session_state.total_requests
eligible = st.session_state.eligible_count
rate     = f"{int(eligible/total*100)}%" if total > 0 else "—"
proc_t   = f"{st.session_state.last_process_time:.1f}s" if st.session_state.last_process_time else "—"

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric("Requests Processed", total, help="This session")
with s2:
    st.metric("Approval Rate", rate, help="Eligible classifications")
with s3:
    st.metric("Last Process Time", proc_t)
with s4:
    st.metric("AI Models", "GPT-4o + mini", help="Vision + analysis")

st.divider()


# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_file(uploaded_file):
    raw = uploaded_file.read()
    return base64.b64encode(raw).decode("utf-8"), uploaded_file.type or "application/octet-stream"


def verify_document(client, b64, mime):
    if mime == "application/pdf":
        content = [
            {"type": "text", "text": (
                "This document was uploaded as proof of nonprofit status. "
                "Does it appear to be a legitimate nonprofit verification document "
                "(e.g. IRS 501c3 determination letter, EIN letter, charity registration)? "
                "Reply ONLY with JSON: {\"verified\": true/false, \"doc_summary\": \"one sentence\"}"
            )},
            {"type": "document", "source": {"type": "base64", "media_type": mime, "data": b64}}
        ]
    else:
        content = [
            {"type": "text", "text": (
                "This image was uploaded as proof of nonprofit status. "
                "Does it appear to be a legitimate nonprofit verification document "
                "(e.g. IRS 501c3 determination letter, EIN letter, charity registration)? "
                "Reply ONLY with JSON: {\"verified\": true/false, \"doc_summary\": \"one sentence\"}"
            )},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
        ]

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=200, temperature=0,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())


def analyze_request(org_name, email, message, has_proof, doc_verified=False, doc_summary=""):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        st.error("⚠️  OPENAI_API_KEY not found.")
        st.stop()

    client = OpenAI(api_key=api_key)

    doc_context = ""
    if doc_summary:
        status = "VERIFIED" if doc_verified else "UNVERIFIED"
        doc_context = f"\nDocument: {doc_summary} [{status}]"

    prompt = f"""You are a SaaS support agent reviewing a nonprofit discount request.

Organization: {org_name}
Email: {email}
Proof checkbox: {has_proof}{doc_context}

Message:
\"\"\"{message}\"\"\"

Return ONLY a valid JSON object with these exact fields:
{{
  "classification": "eligible" | "needs_more_info" | "not_eligible",
  "confidence": <integer 0-100>,
  "reasoning": "2-3 sentence explanation",
  "tone": "brief tone description",
  "risk_flags": ["flag1", "flag2"],
  "suggested_response": "warm professional reply 3-5 sentences",
  "tags": ["tag1", "tag2", "tag3"]
}}

Rules:
- classification eligible: doc verified AND clear nonprofit mission
- classification needs_more_info: missing doc, unverified doc, or unclear mission
- classification not_eligible: commercial/for-profit signals
- confidence: your certainty in the classification (0=very unsure, 100=certain)
- risk_flags: list 0-3 specific concerns. Empty list [] if none.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())


# ── Layout ────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown("#### 📋 Discount Request Form")

    org_name = st.text_input("Organization Name", placeholder="e.g. Green Earth Foundation")
    email    = st.text_input("Contact Email", placeholder="e.g. hello@greenearth.org")
    message  = st.text_area(
        "Request Message",
        placeholder="Describe your organization's mission and why you're requesting a nonprofit discount...",
        height=150,
    )

    st.markdown("**Proof of Nonprofit Status**")
    st.caption("Upload your 501(c)(3) letter, EIN document, or equivalent. Accepts PDF, PNG, JPG.")
    uploaded_doc = st.file_uploader(
        "Upload document",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    has_proof = st.checkbox("✅ I confirm this document is authentic and belongs to our organization")
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("🔍 Analyze Eligibility")


with right_col:
    st.markdown("#### 📊 Eligibility Analysis")

    if not submit:
        st.markdown("""
        <div class="result-placeholder">
            Submit a request to see<br>the AI analysis here.
        </div>
        """, unsafe_allow_html=True)

    else:
        if not org_name.strip() or not message.strip():
            st.warning("Please fill in Organization Name and Request Message.")
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                st.error("⚠️  OPENAI_API_KEY not found.")
                st.stop()

            client       = OpenAI(api_key=api_key)
            t_start      = time.time()
            doc_verified = False
            doc_summary  = ""
            has_doc      = uploaded_doc is not None

            # ── Progress ──
            progress = st.progress(0, text="Starting...")

            # ── Step 1: document verification ──
            if has_doc:
                progress.progress(20, text="🔎 Verifying document...")
                try:
                    b64, mime    = encode_file(uploaded_doc)
                    doc_result   = verify_document(client, b64, mime)
                    doc_verified = doc_result.get("verified", False)
                    doc_summary  = doc_result.get("doc_summary", "Document uploaded")
                except Exception as e:
                    st.warning(f"Document verification failed: {e}")

                if doc_verified:
                    st.markdown(f'<div class="doc-verified">✅ Verified — {doc_summary}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="doc-unverified">⚠️ Not verified — {doc_summary}</div>', unsafe_allow_html=True)

            # ── Step 2: analyze ──
            progress.progress(60, text="🤖 Analyzing eligibility...")
            try:
                result = analyze_request(org_name, email, message, has_proof, doc_verified, doc_summary)
            except json.JSONDecodeError:
                st.error("Unexpected AI response format. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"API error: {e}")
                st.stop()

            t_elapsed = time.time() - t_start
            progress.progress(100, text="✅ Complete!")
            time.sleep(0.4)
            progress.empty()

            st.session_state.total_requests += 1
            st.session_state.last_process_time = t_elapsed
            if result.get("classification") == "eligible":
                st.session_state.eligible_count += 1

            # ── Classification + confidence ──
            classification = result.get("classification", "needs_more_info")
            confidence     = result.get("confidence", 50)

            if classification == "eligible":
                badge = '<span class="status-eligible">✅ Eligible</span>'
            elif classification == "not_eligible":
                badge = '<span class="status-not-eligible">❌ Not Eligible</span>'
            else:
                badge = '<span class="status-needs-review">⚠️ Needs Review</span>'

            st.markdown(badge, unsafe_allow_html=True)

            conf_class = "conf-high" if confidence >= 75 else ("conf-medium" if confidence >= 45 else "conf-low")
            st.markdown(f"""
            <div class="confidence-wrap">
                <div class="confidence-label">AI Confidence</div>
                <div class="confidence-track">
                    <div class="confidence-fill {conf_class}" style="width:{confidence}%"></div>
                </div>
                <div class="confidence-pct">{confidence}%</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Risk flags ──
            risk_flags = result.get("risk_flags", [])
            if risk_flags:
                st.markdown('<div class="section-label">⚑ Risk Flags</div>', unsafe_allow_html=True)
                flags_html = " ".join(f'<span class="risk-flag">⚠ {f}</span>' for f in risk_flags)
                st.markdown(flags_html, unsafe_allow_html=True)

            # ── Reasoning ──
            st.markdown('<div class="section-label">Reasoning</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#333;line-height:1.65;margin:0'>{result.get('reasoning','')}</p>", unsafe_allow_html=True)

            # ── Tone ──
            st.markdown('<div class="section-label">Request Tone</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.88rem;color:#666;font-style:italic;margin:0'>{result.get('tone','')}</p>", unsafe_allow_html=True)

            # ── Suggested response + copy button ──
            st.markdown('<div class="section-label">Suggested Response</div>', unsafe_allow_html=True)
            suggested = result.get("suggested_response", "")
            st.markdown(f'<div class="response-box">{suggested}</div>', unsafe_allow_html=True)
            st.code(suggested, language=None)

            # ── Tags ──
            tags = result.get("tags", [])
            if tags:
                st.markdown('<div class="section-label">Tags</div>', unsafe_allow_html=True)
                st.markdown(" ".join(f'<span class="tag">{t}</span>' for t in tags), unsafe_allow_html=True)

            st.markdown(f'<div class="process-time">⏱ Processed in {t_elapsed:.1f}s</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("AI Nonprofit Discount Assistant · Streamlit + OpenAI GPT-4o · Internal Support Tool")
