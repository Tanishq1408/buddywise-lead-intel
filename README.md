# 🦺 Buddywise Lead Intelligence Platform

> AI-powered sales qualification tool built for the Buddywise Working Student Case Study.
> Paste an inbound email → get a priority verdict, company profile, person intelligence, buying signals, and a personalised outreach plan — in 5 seconds.

## What It Does

A Buddywise salesperson receives 50+ emails per day. Most are noise. Figuring out which ones matter — and how to approach them — takes 15–20 minutes of manual research per lead.

This tool eliminates that friction entirely.

**Input:** Name + Email + optional company name

**Output:**
- 🚀 Priority verdict (FAST TRACK / PURSUE / QUALIFY / NURTURE / DEPRIORITISE)
- Company fit score (0–100) based on Buddywise's actual ICP
- Person score (0–100) based on decision authority and seniority
- Buying signals with strength scoring (HOT / WARM / LUKEWARM / COLD)
- Personalised subject line and opening angle
- Specific research hook and recommended next step
- Caution flags and contact strategy

## Tech Stack

- **Frontend:** Streamlit
- **AI Engine:** Anthropic Claude (claude-sonnet-4-6)
- **Language:** Python 3.9+

## Setup (Local)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/buddywise-lead-intel
cd buddywise-lead-intel

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
# Edit .streamlit/secrets.toml and replace with your key:
# ANTHROPIC_API_KEY = "sk-ant-..."

# 4. Run
streamlit run app.py
```

## Deployment

Deployed on Streamlit Community Cloud. Add `ANTHROPIC_API_KEY` in the Secrets section of the Streamlit dashboard.

## Author

**Tanishq Singh** — MSc Project Management & Data Science @ HTW Berlin
Built specifically for the Buddywise Working Student (Tech & Ops) case study interview.
