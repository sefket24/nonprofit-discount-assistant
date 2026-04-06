# Nonprofit Discount Assistant

**A browser-based AI support tool for evaluating nonprofit discount requests — inspired by real SaaS support workflows.**

🔗 **[Live Demo](https://your-username.github.io/nonprofit-discount-assistant)**
> Replace `your-username` with your actual GitHub username after deployment.

---

## Overview

This project simulates an internal support tool used by SaaS teams to handle incoming nonprofit discount requests. Instead of manual review for every ticket, the assistant uses AI to classify requests, detect tone, and draft an empathetic response — all in real time.

Built as a single-page app that runs entirely in the browser. No backend required.

---

## Problem

Support teams at SaaS companies receive high volumes of repetitive discount requests — many from nonprofits seeking reduced pricing. Each one requires:

- Verifying eligibility criteria
- Assessing the tone and urgency of the request
- Drafting a thoughtful, on-brand response

This process is slow, inconsistent, and hard to scale. A support rep reviewing 40 tickets a day will inevitably apply different standards to similar requests.

---

## Solution

This tool provides a lightweight AI layer that:

1. Accepts a support request via a structured input form
2. Sends the request to Claude (Anthropic's AI) with a structured prompt
3. Returns a JSON evaluation with classification, reasoning, tone, confidence score, and a suggested reply
4. Displays everything in a clean, internal-tool-style UI

The result is a consistent first pass on every request — support reps can accept, edit, or override the suggestion, but they're never starting from a blank page.

---

## How It Works

```
User fills out form
        ↓
Request is sent to Anthropic API (claude-sonnet)
        ↓
AI returns structured JSON:
  - classification: eligible / needs_more_info / not_eligible
  - reasoning: 1–2 sentence explanation
  - tone: frustrated / neutral / polite
  - confidence: 0–100 score
  - suggested_response: draft reply for the support rep
  - tags: e.g. ["billing", "nonprofit", "discount"]
        ↓
UI renders result with status badge, confidence bar, and copyable response
```

The prompt is designed to mimic how a senior support rep would evaluate requests: accounting for proof of status, message tone, and likely intent.

---

## Example Input / Output

**Input:**

| Field | Value |
|---|---|
| Organization | Riverside Youth Literacy Program |
| Email | director@riversidelivs.org |
| Message | "Hi, we're a small 501(c)(3) serving underserved kids in our area. We'd love to use your platform but the standard pricing is out of reach for us. Do you offer nonprofit discounts?" |
| Proof available | ✅ Yes |

**Output:**

```json
{
  "classification": "eligible",
  "reasoning": "The organization identifies as a registered 501(c)(3) and has indicated proof is available. The request is clearly mission-driven and fits standard nonprofit discount criteria.",
  "tone": "polite",
  "confidence": 91,
  "suggested_response": "Thank you for reaching out — we love supporting organizations doing this kind of work. Since you have your 501(c)(3) documentation ready, please reply with it attached and we'll get your nonprofit discount applied within 1–2 business days.",
  "tags": ["nonprofit", "discount", "billing", "eligible"]
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML, CSS, JavaScript |
| AI | Anthropic Claude API (`claude-sonnet-4`) |
| Fonts | Sora + IBM Plex Mono (Google Fonts) |
| Hosting | GitHub Pages |

No frameworks, no build step, no backend. The entire app is a single `index.html` file that calls the Anthropic API directly from the browser.

---

## Running Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/nonprofit-discount-assistant.git
   cd nonprofit-discount-assistant
   ```

2. Open `index.html` in your browser — no install needed.

3. Enter your [Anthropic API key](https://console.anthropic.com) in the form to activate the AI.

> Your API key is used only in your browser session and is never stored or transmitted anywhere except directly to Anthropic's API.

---

## Inspiration

This project is inspired by real workflows I encountered working with SaaS support teams — specifically around the challenge of handling high-volume, structured requests like nonprofit discount applications consistently and empathetically at scale.

The goal was to explore how a lightweight AI layer could assist (not replace) support reps by providing a reliable first pass on incoming requests.

---

## Future Ideas

- Save and export evaluation history
- Confidence threshold routing (auto-approve above 85%, escalate below 50%)
- Integration with Zendesk or Intercom via webhook
- Team-level analytics dashboard
