"""
Buddywise Lead Intelligence — API Layer
Supports: Anthropic Claude + Google Gemini
"""

import json, re
from buddywise_context import BUDDYWISE_DESCRIPTION

def extract_domain(email):
    return email.strip().split("@")[1].lower() if "@" in email else email.strip()

def is_personal_email(email):
    personal = {"gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com",
                 "me.com","gmx.com","gmx.de","web.de","proton.me","protonmail.com","aol.com"}
    return extract_domain(email) in personal

def is_generic_email(email):
    generic = {"info","contact","hello","office","admin","support","sales",
                "marketing","hr","careers","jobs","press","media","team","general"}
    return email.split("@")[0].lower() in generic

def _system_prompt():
    return f"""You are a sales intelligence analyst for Buddywise — AI-powered workplace safety platform.

{BUDDYWISE_DESCRIPTION}

━━━ COMPANY FIT SCORE (0-100) ━━━
Industry Fit (0-40):
  TIER 1 (36-40): Chemical, petrochemical, oil/gas, heavy manufacturing, machine tools, automotive mfg, mining, pulp/paper, energy/power, ports, infrastructure construction
  TIER 2 (26-35): Food manufacturing, pharma mfg, construction, logistics/warehousing with forklifts, medical device mfg, waste management
  TIER 3 (16-25): General logistics, healthcare, large retail with warehouses
  TIER 4 (6-15): Restaurants, consumer food service, retail, media, education
  TIER 5 (0-5): Software/SaaS, banking, consulting, professional services

Company Size (0-25): 50k+→25, 10-50k→22, 1-10k→18, 200-1k→12, 50-200→5, <50→0
Geography (0-20): DACH→20, Nordics→19, UK/Benelux→16, Core EU→14, Rest EU→11, N.America→8, Other→4
Physical Risk (0-15): Multiple hazardous sites→15, Factories/plants→12, Mixed→8, Office-only→2, Unknown→6

━━━ PERSON SCORE (0-100) — REALISTIC BUYING LOGIC ━━━

WHO ACTUALLY MAKES BUYING DECISIONS FOR SAFETY TOOLS:
The person who SELECTS and RECOMMENDS a safety tool is almost never the CEO.
It is the EHS/Safety Manager, Plant Manager, or Operations Manager — the people who live with the problem daily.
Procurement makes the decision to purchase once someone else chose the tool.
CEOs and C-Suite are influential but rarely the initiating buyer.

Decision Authority (0-50):
  OPERATIONAL BUYERS — they choose the tool:
    EHS Manager / HSE Manager / Safety Manager / QHSE Manager: 50
    Head of EHS / Director of EHS / VP EHS: 49
    Plant Manager / Facility Manager / Site Manager: 47
    Operations Manager / Production Manager: 45
    Procurement Manager / Purchasing Manager (inbound = someone already chose): 44
  INFLUENTIAL — can accelerate or approve but don't typically initiate:
    COO / Chief Operations Officer: 40
    CEO / President / Managing Director: 35
    CFO / Chief Financial Officer: 30
    VP Operations / Operations Director: 38
    Engineering Manager / Technical Director: 28
    HR Director / Head of HR: 22
    Sustainability Director / ESG Manager: 20
    Risk Manager / Compliance Manager: 20
  CONNECTORS — route you to the right person:
    IT Manager / IT Director / CTO: 12
    Marketing / Communications / PR: 5
    Sales / Business Development: 6
    Administrative / Coordinator / Assistant: 3
    Unknown / Unclear: 10

Seniority (0-30): C-Suite→28, VP→24, Director→20, Sr Manager→15, Manager→12, Individual→5, Unknown→8
Engagement Signal (0-20): Operational buyer inbound→20, Procurement inbound→18, C-Suite inbound→15, Influencer inbound→12, Cold/unknown→8

PERSON TIER RULES:
  DECISION MAKER (score 65-100): The person who will actually select and recommend this tool
  INFLUENTIAL (score 40-64): Can open doors, approve budget, or block — but rarely initiates tool selection
  CONNECTOR (score 0-39): Routes you to the right person, positive relationship worth maintaining

━━━ BUYING SIGNALS ━━━
CRITICAL (+25): new operational leader <18mo, recent workplace accident, new site/expansion announced, safety team actively hiring, procurement contact inbound
HIGH (+15): ESG report with safety targets, industry peer accident, regulatory audit cycle, M&A/restructuring, Industry 4.0 programme
MEDIUM (+8): rapid growth, cost reduction drive, Atlas Copco/Ramudden connection

━━━ PRIORITY RULES ━━━
FAST_TRACK: Company≥80 AND Person≥65
PURSUE: Company≥65 AND Person≥45
QUALIFY: Company≥40
NURTURE: Company<40 AND Person≥65
DEPRIORITISE: both low

━━━ SALES ACTION — KEEP IT MINIMAL ━━━
Return ONLY what a rep needs to act immediately:
- One subject line (specific, not generic)
- One opening angle (the main pain point to lead with)
- One next step (the exact action to take)
- One caution flag only if critical (omit if minor)

Return ONLY valid JSON, no markdown."""

def _user_prompt(name, email, company):
    domain = extract_domain(email)
    personal = is_personal_email(email)
    generic = is_generic_email(email)
    co = company or f"Infer from domain: {domain}"
    return f"""Analyse this Buddywise inbound lead:
Name: {name} | Email: {email} | Domain: {domain} | Company: {co}
Personal email: {personal} | Generic email: {generic}

Return this JSON exactly:
{{
  "company": {{
    "name": "",
    "industry": "",
    "industry_tier": "TIER_1|TIER_2|TIER_3|TIER_4|TIER_5",
    "size_employees": "",
    "revenue_estimate": "",
    "headquarters": "",
    "countries_operating": [],
    "physical_operations": "",
    "known_hazards": [],
    "buddywise_relevant_features": [],
    "fit_score": 0,
    "fit_label": "STRONG FIT|GOOD FIT|POSSIBLE FIT|WEAK FIT|NOT A FIT",
    "fit_reasoning": "",
    "score_breakdown": {{"industry_fit": 0, "company_size": 0, "geography": 0, "physical_site_risk": 0}}
  }},
  "person": {{
    "name": "{name}",
    "likely_role": "",
    "department": "",
    "seniority_level": "C_SUITE|VP|DIRECTOR|SENIOR_MANAGER|MANAGER|INDIVIDUAL|UNKNOWN",
    "decision_authority": "",
    "budget_relevance": "HIGH|MEDIUM|LOW|UNKNOWN",
    "person_score": 0,
    "person_tier": "DECISION_MAKER|INFLUENTIAL|CONNECTOR",
    "tier_reasoning": "",
    "key_insight": "",
    "score_breakdown": {{"decision_authority": 0, "seniority": 0, "engagement_signal": 0}}
  }},
  "buying_signals": [
    {{"signal_name": "", "strength": "CRITICAL|HIGH|MEDIUM", "score": 25, "evidence": ""}}
  ],
  "buying_signal_total": 0,
  "buying_signal_label": "HOT|WARM|LUKEWARM|COLD",
  "sales_action": {{
    "priority": "FAST_TRACK|PURSUE|QUALIFY|NURTURE|DEPRIORITISE",
    "priority_reasoning": "",
    "subject_line": "",
    "opening_angle": "",
    "next_step": "DEMO_REQUEST|DISCOVERY_CALL|CONTENT_SEND|LINKEDIN_CONNECT|FIND_CHAMPION",
    "next_step_text": "",
    "critical_caution": ""
  }},
  "confidence": {{
    "company_confidence": "HIGH|MEDIUM|LOW|UNKNOWN",
    "person_confidence": "HIGH|MEDIUM|LOW|UNKNOWN",
    "data_notes": "",
    "is_personal_email": {str(personal).lower()},
    "is_generic_email": {str(generic).lower()}
  }}
}}"""

def _parse(text):
    if "```" in text:
        text = re.sub(r"```(?:json)?\n?", "", text).replace("```", "").strip()
    s, e = text.find("{"), text.rfind("}") + 1
    if s != -1 and e > s:
        text = text[s:e]
    return json.loads(text)

def analyse_lead_claude(api_key, name, email, company=None):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2000, temperature=0,
        system=_system_prompt(),
        messages=[{"role": "user", "content": _user_prompt(name, email, company)}]
    )
    return _parse(msg.content[0].text.strip())

def analyse_lead_gemini(api_key, name, email, company=None):
    from google import genai
    client = genai.Client(api_key=api_key)
    prompt = _system_prompt() + "\n\n" + _user_prompt(name, email, company)
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return _parse(response.text.strip())

def analyse_lead(api_key, name, email, company=None, provider="claude"):
    if provider == "gemini":
        return analyse_lead_gemini(api_key, name, email, company)
    return analyse_lead_claude(api_key, name, email, company)
