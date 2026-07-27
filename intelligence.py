"""Buddywise Lead Intelligence — API Layer"""

import json, re
from buddywise_context import BUDDYWISE_DESCRIPTION

def extract_domain(email):
    return email.strip().split("@")[1].lower() if "@" in email else email.strip()

def is_personal_email(email):
    return extract_domain(email) in {"gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","me.com","gmx.com","gmx.de","web.de","proton.me","protonmail.com","aol.com"}

def is_generic_email(email):
    return email.split("@")[0].lower() in {"info","contact","hello","office","admin","support","sales","marketing","hr","careers","jobs","press","media","team","general"}

def _repair_json(text):
    """Attempt to close truncated JSON by balancing braces/brackets."""
    stack = []
    in_str = False
    esc = False
    result = list(text)
    for ch in text:
        if esc:            esc = False; continue
        if ch == '\\' and in_str: esc = True; continue
        if ch == '"':      in_str = not in_str; continue
        if not in_str:
            if ch in '{[': stack.append('}' if ch == '{' else ']')
            elif ch in '}]' and stack: stack.pop()
    close = ''.join(reversed(stack))
    if close: return text.rstrip() + close
    return text

def _parse(text):
    """Robust JSON extractor with repair fallback."""
    # Strip markdown fences
    if '```' in text:
        text = re.sub(r'```(?:json)?\n?', '', text).replace('```', '').strip()
    # Find JSON object start
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object in response")
    text = text[start:]
    # Try 1: raw_decode (handles trailing text)
    try:
        obj, _ = json.JSONDecoder().raw_decode(text)
        return obj
    except json.JSONDecodeError:
        pass
    # Try 2: repair truncated JSON then parse
    try:
        return json.loads(_repair_json(text))
    except json.JSONDecodeError:
        pass
    # Try 3: find last complete top-level field and close
    last_comma = text.rfind(',"')
    if last_comma > 0:
        try:
            return json.loads(_repair_json(text[:last_comma] + '}'))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not parse JSON. Response length: {len(text)}")

def _build_prompt(name, email, company):
    domain  = extract_domain(email)
    personal= is_personal_email(email)
    generic = is_generic_email(email)
    co      = company or f"infer from {domain}"

    return f"""You are a sales intelligence analyst for Buddywise — AI workplace safety via computer vision.
Buddywise detects PPE violations, zone breaches, vehicle hazards, person-down using existing cameras + Buddy Box edge device.
Sells to: manufacturing, chemical, mining, logistics, construction, energy companies with 200+ workers on physical sites.
Active markets: DACH, Nordics, UK, Poland.

LEAD: Name={name} | Email={email} | Domain={domain} | Company={co} | PersonalEmail={personal} | GenericEmail={generic}

SCORING RULES:

Company fit (0-100):
  Industry(0-40): chemical/mining/heavy-mfg/oil-gas=38-40 | food-mfg/pharma/construction/logistics=27-35 | healthcare/warehouse-retail=16-25 | restaurants/retail/media=6-15 | software/finance/consulting=0-5
  Size(0-25): 50k+=25, 10-50k=22, 1-10k=18, 200-1k=12, 50-200=5, <50=0
  Geography(0-20): DACH=20, Nordics=19, UK/Benelux=16, CoreEU=14, RestEU=11, Americas=8, Other=4
  PhysicalRisk(0-15): multi-hazardous-sites=15, factories=12, mixed=8, office=2
  FitLabel: 80-100=STRONG FIT, 60-79=GOOD FIT, 40-59=POSSIBLE FIT, 20-39=WEAK FIT, 0-19=NOT A FIT

Person score (0-100):
  DECISION_MAKER (65+): people who SELECT and IMPLEMENT the safety tool
    EHS/HSE/Safety/QHSE Manager=50 | Head/Director/VP of EHS=49 | CSO=50
    Plant/Facility/Site Manager=47 | Operations/Production Manager=45
    Procurement Manager (inbound=eval already decided)=44
  INFLUENTIAL (40-64): C-suite who APPROVE budget but do NOT choose the tool
    COO=40 | CEO/President/MD/Chairman=35 | CFO=28 | VP-Operations-strategic=35
    EngineeringDirector=25 | HRDirector=18 | SustainabilityDir=18
  CONNECTOR (<40): routes you to the right person
    IT/CTO=12 | Marketing/PR=5 | Sales/BD=6 | Admin=3 | Unknown=10
  Seniority(0-30): C-Suite=28, VP=24, Director=20, SrMgr=15, Mgr=12, Individual=5
  Signal(0-20): operational-buyer-inbound=20, procurement-inbound=18, c-suite-inbound=14, influencer=11, cold=8
  RULE: CEO/COO/CFO are ALWAYS INFLUENTIAL. EHS/Safety/Ops managers are ALWAYS DECISION_MAKER.

Buying signals:
  CRITICAL+25: new leader <18mo, recent accident, new site/expansion, safety hiring, procurement inbound
  HIGH+15: ESG safety targets, peer accident, regulatory audit, M&A, Industry4.0 programme
  MEDIUM+8: rapid growth, cost reduction, Atlas Copco/Ramudden connection
  SignalLabel: 60+=HOT, 35-59=WARM, 10-34=LUKEWARM, 0-9=COLD

Priority (pick ONE):
  FAST_TRACK: Company>=80 AND Person>=65
  PURSUE: Company>=50 OR (Company>=40 AND Person>=65)
  NURTURE: Company<40 AND Person>=65
  DEPRIORITISE: everything else

IMPORTANT: Keep ALL string values under 80 characters. Be concise. Return ONLY valid JSON.

{{
  "company": {{
    "name": "",
    "industry": "",
    "industry_tier": "",
    "size_employees": "",
    "revenue_estimate": "",
    "headquarters": "",
    "countries_operating": [],
    "physical_operations": "",
    "known_hazards": [],
    "buddywise_relevant_features": [],
    "fit_score": 0,
    "fit_label": "",
    "fit_reasoning": "",
    "score_breakdown": {{"industry_fit":0,"company_size":0,"geography":0,"physical_site_risk":0}}
  }},
  "person": {{
    "name": "{name}",
    "likely_role": "",
    "department": "",
    "seniority_level": "",
    "decision_authority": "",
    "budget_relevance": "",
    "person_score": 0,
    "person_tier": "",
    "tier_reasoning": "",
    "key_insight": "",
    "score_breakdown": {{"decision_authority":0,"seniority":0,"engagement_signal":0}}
  }},
  "buying_signals": [
    {{"signal_name":"","strength":"","score":0,"evidence":""}}
  ],
  "buying_signal_total": 0,
  "buying_signal_label": "",
  "sales_action": {{
    "priority": "",
    "priority_reasoning": "",
    "subject_line": "",
    "opening_angle": "",
    "next_step": "",
    "next_step_text": "",
    "critical_caution": ""
  }},
  "confidence": {{
    "company_confidence": "",
    "person_confidence": "",
    "overall_confidence": "",
    "data_notes": "",
    "is_personal_email": {str(personal).lower()},
    "is_generic_email": {str(generic).lower()}
  }}
}}"""

def analyse_lead_claude(api_key, name, email, company=None):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    for attempt in range(2):  # retry once on failure
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            temperature=0,
            messages=[{"role":"user","content":_build_prompt(name,email,company)}]
        )
        try:
            return _parse(msg.content[0].text.strip())
        except Exception as e:
            if attempt == 0: continue
            raise e

def analyse_lead_gemini(api_key, name, email, company=None):
    from google import genai
    client = genai.Client(api_key=api_key)
    for attempt in range(2):
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=_build_prompt(name,email,company)
        )
        try:
            return _parse(response.text.strip())
        except Exception as e:
            if attempt == 0: continue
            raise e

def analyse_lead(api_key, name, email, company=None, provider="claude"):
    if provider == "gemini":
        return analyse_lead_gemini(api_key, name, email, company)
    return analyse_lead_claude(api_key, name, email, company)
