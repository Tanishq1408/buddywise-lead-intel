"""
Buddywise Lead Intelligence — Claude API Layer & Scoring Engine
"""

import anthropic
import json
import re
from buddywise_context import (
    BUDDYWISE_DESCRIPTION, INDUSTRY_SCORING, PERSON_ROLE_SCORING,
    GEOGRAPHY_SCORING, BUYING_SIGNAL_FRAMEWORK, PRIORITY_MATRIX,
    PERSONAL_EMAIL_DOMAINS, GENERIC_EMAIL_PREFIXES
)


# ── EMAIL UTILITIES ─────────────────────────────────────────────────────────────

def extract_domain(email: str) -> str:
    if "@" not in email:
        return email.strip()
    return email.strip().split("@")[1].lower()


def is_personal_email(email: str) -> bool:
    return extract_domain(email) in PERSONAL_EMAIL_DOMAINS


def is_generic_email(email: str) -> bool:
    prefix = email.strip().split("@")[0].lower()
    return prefix in GENERIC_EMAIL_PREFIXES


# ── PROMPT BUILDER ──────────────────────────────────────────────────────────────

def build_system_prompt() -> str:
    return f"""You are a senior sales intelligence analyst for Buddywise — an AI-powered workplace safety platform. Your only job is to analyse inbound sales leads and return precise, structured JSON intelligence that helps a salesperson make an immediate, confident decision about whether to pursue this lead and exactly how to approach them.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUDDYWISE COMPLETE CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{BUDDYWISE_DESCRIPTION}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPANY FIT SCORING RULES (Total: 0-100)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INDUSTRY FIT (0-40 points):
TIER 1 (36-40): Chemical, petrochemical, oil/gas, heavy manufacturing, machine tools, automotive mfg, aerospace, steel/metal, mining, pulp/paper, energy/power, ports, shipbuilding, semiconductor mfg, infrastructure construction
TIER 2 (26-35): Food & beverage manufacturing, pharma manufacturing, medical device mfg, waste management, logistics/warehousing, general construction, agriculture at scale, glass/rubber/packaging manufacturing
TIER 3 (16-25): General logistics/courier, hospital/healthcare, large retail with warehouses, furniture manufacturing
TIER 4 (6-15): Restaurants, consumer food service, fashion retail, hospitality, media, education
TIER 5 (0-5): Software/SaaS, banking/finance/insurance, marketing agencies, consulting, professional services

COMPANY SIZE (0-25 points):
- 50,000+ employees: 25
- 10,000-49,999: 22
- 1,000-9,999: 18
- 200-999: 12
- 50-199: 5
- Under 50: 0

GEOGRAPHY (0-20 points):
- Germany, Austria, Switzerland (DACH): 20
- Sweden, Finland, Norway, Denmark (Nordics): 19
- UK, Netherlands, Belgium, Ireland: 16
- France, Spain, Italy, Poland, Czech Republic, Hungary: 14
- Other EU countries: 11
- USA, Canada: 8
- Rest of world: 4

PHYSICAL SITE RISK (0-15 points):
- Multiple known high-risk industrial sites (chemicals, machinery, mining): 15
- Confirmed factories, plants, or construction sites: 12
- Mixed operations (some physical, some office): 8
- Primarily office-based with minor physical component: 3
- Pure office / digital: 0
- Unknown: 6 (benefit of doubt)

FIT LABELS:
- 80-100: STRONG FIT
- 60-79: GOOD FIT
- 40-59: POSSIBLE FIT
- 20-39: WEAK FIT
- 0-19: NOT A FIT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERSON SCORING RULES (Total: 0-100)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DECISION AUTHORITY (0-50 points):
- Chief Safety Officer / CSO / VP EHS / Head of EHS / HSE Director: 50 ← perfect buyer
- COO / VP Operations / Operations Director: 47
- Plant Manager / Facility Director / Site Manager / Manufacturing Director: 44
- CEO / President / Managing Director: 42
- CFO / VP Finance: 35
- Safety Manager / EHS Manager: 30
- Operations Manager / Production Manager: 28
- HR Director / Head of HR: 22
- Sustainability Director / ESG Manager: 20
- Risk Manager / Compliance Manager: 20
- Engineering Manager: 18
- Procurement Manager / Purchasing Manager: 15 ← signals someone already requested it
- IT Manager / IT Director: 12
- CTO: 14
- Marketing / Sales / Communications: 5
- Unknown / unclear: 10

SENIORITY (0-30 points):
- C-Suite (CEO, COO, CFO, CTO, CSO, CPO, CHRO): 30
- SVP / EVP: 28
- VP / Vice President: 25
- Director: 20
- Senior Manager: 15
- Manager: 10
- Individual Contributor / Analyst / Associate: 5
- Unknown: 8

ENGAGEMENT SIGNAL (0-20 points):
- C-Suite or EHS leader inbound (they came to us): 20
- Procurement inbound (evaluation already in progress): 18
- Director/VP influencer inbound: 14
- Manager-level inbound: 10
- Cold / unknown: 8

PERSON TIER LABELS:
- 75-100: CHAMPION (decision maker with budget authority — prioritise immediately)
- 50-74: INFLUENCER (shapes decision, find the real champion)
- 25-49: GATEKEEPER (routes communication, needs nurturing)
- 0-24: UNKNOWN (need more qualification)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUYING SIGNAL FRAMEWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: +25 per CRITICAL signal, +15 per HIGH signal, +8 per MEDIUM signal. Cap at 100.

CRITICAL SIGNALS (+25 each):
1. New executive or EHS leader hired < 18 months ago — new leaders want quick wins and have political capital
2. Recent publicly reported workplace accident or fatality at this company
3. Announced new site, factory expansion, or major capital project
4. Company actively hiring EHS/safety roles (signals active budget)
5. Procurement is the contact — means someone internally already requested it, you may be in final evaluation

HIGH SIGNALS (+15 each):
6. Published ESG/sustainability report with specific safety reduction targets
7. Industry peer had a major publicised accident (competitive fear)
8. Known regulatory audit cycle or compliance deadline approaching
9. Recent merger, acquisition, or major restructuring
10. Announced Industry 4.0, smart factory, or digital transformation programme

MEDIUM SIGNALS (+8 each):
11. Connected to Buddywise investor network (Atlas Copco, Ramudden, SKF)
12. Announced cost reduction or efficiency programme (safety ROI argument is easier)
13. Rapid site or headcount growth (more workers = more exposure)

BUYING SIGNAL LABELS:
- 60-100: HOT (time-sensitive opportunity — move now)
- 35-59: WARM (good timing, move within 24 hours)
- 10-34: LUKEWARM (no immediate trigger, normal sales cycle)
- 0-9: COLD (no signal detected)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIORITY DECISION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FAST_TRACK: Company ≥ 80 AND Person ≥ 70 (reply within 1 hour)
PURSUE: Company ≥ 65 AND Person ≥ 50 (reply within 24 hours)
QUALIFY: Company ≥ 40, OR Company ≥ 65 with weak person (gather info within 48 hours)
NURTURE: Company < 40 AND Person ≥ 70 (good contact, weak company — keep warm)
DEPRIORITISE: Company < 40 AND Person < 50 (acknowledge and move on)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EDGE CASE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Personal email (@gmail etc): Flag it. Still analyse what you can from the name.
- Generic prefix (info@, contact@): Flag as routing email — this is not a personal contact.
- Unknown/small company: Lower confidence score. Note limited data.
- Software/tech companies: NOT A FIT unless they have significant physical operations (data centres etc).
- Food industry: DISTINGUISH between consumer food service (restaurants = Tier 4) vs food manufacturing (factories = Tier 2).
- Healthcare: DISTINGUISH between office-based clinics (Tier 4) vs pharmaceutical manufacturing (Tier 2).
- DHL/logistics: Score as Tier 2 — large warehouses with forklifts = real safety risk, not pure Tier 1.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES FOR OUTPUT QUALITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Be SPECIFIC and FACTUAL — use real knowledge about named companies and executives
2. For major companies (BASF, TRUMPF, DHL, Sandvik etc) — use accurate real data
3. The "specific_hook" MUST be genuinely specific — reference a real facility, real expansion, real event, real product line
4. Buying signals should reflect REAL WORLD knowledge about this company's actual situation
5. Procurement contacts are HIGH PRIORITY — signal that evaluation is already in progress
6. New executives (< 18 months) are your MOST VALUABLE buying signal — mention their appointment date
7. The suggested_subject_line must be personalised to this exact company — never generic
8. Always calculate scores numerically — no rounding except to whole numbers

RETURN ONLY VALID JSON. NO MARKDOWN. NO EXPLANATION. NO PREAMBLE. JUST THE JSON OBJECT."""


def build_user_prompt(name: str, email: str, company: str = None) -> str:
    domain = extract_domain(email)
    personal_flag = is_personal_email(email)
    generic_flag = is_generic_email(email)

    company_hint = company if company else f"Infer from domain: {domain}"

    return f"""Analyse this inbound lead for Buddywise. Return the JSON object with all fields populated.

LEAD DATA:
- Name: {name}
- Email: {email}
- Domain: {domain}
- Company: {company_hint}
- Personal email detected: {personal_flag}
- Generic/routing email detected: {generic_flag}

REQUIRED JSON OUTPUT STRUCTURE:

{{
  "company": {{
    "name": "full official company name",
    "industry": "specific industry description (e.g. 'Chemical Manufacturing' not just 'Manufacturing')",
    "industry_tier": "TIER_1|TIER_2|TIER_3|TIER_4|TIER_5",
    "size_employees": "exact number or best estimate as string (e.g. '111,000' or '~5,000')",
    "revenue_estimate": "annual revenue with currency (e.g. '€78.7B' or '~€2B')",
    "headquarters": "City, Country",
    "countries_operating": ["list all countries with major operations"],
    "physical_operations": "specific description of physical industrial operations relevant to Buddywise",
    "known_hazards": ["specific safety hazards at this company — be precise"],
    "buddywise_relevant_features": ["which specific Buddywise features apply to this company"],
    "fit_score": 0,
    "fit_label": "STRONG FIT|GOOD FIT|POSSIBLE FIT|WEAK FIT|NOT A FIT",
    "fit_reasoning": "2-3 sentences explaining the score based on Buddywise ICP",
    "score_breakdown": {{
      "industry_fit": 0,
      "company_size": 0,
      "geography": 0,
      "physical_site_risk": 0
    }}
  }},
  "person": {{
    "name": "{name}",
    "likely_role": "their most likely current job title — be specific",
    "department": "EHS|Operations|C-Suite|Finance|IT|HR|Procurement|Sales|Marketing|Engineering|Unknown",
    "seniority_level": "C_SUITE|VP|DIRECTOR|SENIOR_MANAGER|MANAGER|INDIVIDUAL|UNKNOWN",
    "decision_authority": "specific description of their buying authority and budget access",
    "is_ehs_relevant": true,
    "budget_relevance": "HIGH|MEDIUM|LOW|UNKNOWN",
    "person_score": 0,
    "person_tier": "CHAMPION|INFLUENCER|GATEKEEPER|UNKNOWN",
    "tier_reasoning": "why this person is classified this way — be specific",
    "key_insight": "one specific insight about this person that a salesperson should know",
    "score_breakdown": {{
      "decision_authority": 0,
      "seniority": 0,
      "engagement_signal": 0
    }}
  }},
  "buying_signals": [
    {{
      "signal_name": "short signal name",
      "strength": "CRITICAL|HIGH|MEDIUM",
      "score": 25,
      "evidence": "specific evidence for why this signal applies to this company/person right now"
    }}
  ],
  "buying_signal_total": 0,
  "buying_signal_label": "HOT|WARM|LUKEWARM|COLD",
  "sales_action": {{
    "priority": "FAST_TRACK|PURSUE|QUALIFY|NURTURE|DEPRIORITISE",
    "priority_reasoning": "concise 1-2 sentence explanation of why this priority was assigned",
    "suggested_subject_line": "personalised email subject — must reference this specific company or person detail",
    "opening_angle": "the specific pain point or opportunity to lead with for this company",
    "specific_hook": "one genuinely specific, researched detail to mention — a real facility, real expansion, real product line, real recent event",
    "suggested_next_step": "DEMO_REQUEST|DISCOVERY_CALL|CONTENT_SEND|LINKEDIN_CONNECT|SENIOR_BDR_ESCALATE",
    "next_step_detail": "specific text of what to do (e.g. 'Request a 20-min discovery call focused on their Ludwigshafen chemical complex')",
    "caution_flags": ["list of things to be aware of when approaching this lead"],
    "ideal_contact_strategy": "specific advice on how to approach this person given their role and seniority"
  }},
  "confidence": {{
    "company_confidence": "HIGH|MEDIUM|LOW|UNKNOWN",
    "person_confidence": "HIGH|MEDIUM|LOW|UNKNOWN",
    "overall_confidence": "HIGH|MEDIUM|LOW|UNKNOWN",
    "data_notes": "what is confirmed vs inferred — be transparent",
    "is_personal_email": {str(personal_flag).lower()},
    "is_generic_email": {str(generic_flag).lower()},
    "recommendation_note": "any important caveat the salesperson should know"
  }}
}}"""


# ── PRIORITY CALCULATOR ─────────────────────────────────────────────────────────

def calculate_priority(company_score: int, person_score: int, signal_total: int) -> str:
    if company_score >= 80 and person_score >= 70:
        return "FAST_TRACK"
    elif company_score >= 65 and person_score >= 50:
        return "PURSUE"
    elif company_score >= 40:
        return "QUALIFY"
    elif company_score < 40 and person_score >= 70:
        return "NURTURE"
    else:
        return "DEPRIORITISE"


# ── MAIN API CALL ───────────────────────────────────────────────────────────────

def analyse_lead(api_key: str, name: str, email: str, company: str = None) -> dict:
    """
    Call Claude API with Buddywise context and return parsed lead intelligence.
    Returns a dict with the full analysis.
    """
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        temperature=0,
        system=build_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(name, email, company)
            }
        ]
    )

    response_text = message.content[0].text.strip()

    # Strip markdown code fences if present
    if "```" in response_text:
        response_text = re.sub(r"```(?:json)?\n?", "", response_text)
        response_text = re.sub(r"```", "", response_text)
        response_text = response_text.strip()

    # Find JSON object boundaries
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start != -1 and end > start:
        response_text = response_text[start:end]

    result = json.loads(response_text)

    # Override priority with our deterministic calculator as safety net
    company_score = result.get("company", {}).get("fit_score", 0)
    person_score = result.get("person", {}).get("person_score", 0)
    signal_total = result.get("buying_signal_total", 0)
    calculated_priority = calculate_priority(company_score, person_score, signal_total)

    # Only override if Claude's priority differs significantly
    claude_priority = result.get("sales_action", {}).get("priority", calculated_priority)
    result["sales_action"]["priority"] = calculated_priority if claude_priority != calculated_priority else claude_priority

    return result
