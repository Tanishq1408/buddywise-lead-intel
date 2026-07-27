"""Buddywise Lead Intelligence — API Layer (optimised for speed)"""

import json, re
from buddywise_context import BUDDYWISE_DESCRIPTION

def extract_domain(email):
    return email.strip().split("@")[1].lower() if "@" in email else email.strip()

def is_personal_email(email):
    return extract_domain(email) in {"gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","me.com","gmx.com","gmx.de","web.de","proton.me","protonmail.com","aol.com"}

def is_generic_email(email):
    return email.split("@")[0].lower() in {"info","contact","hello","office","admin","support","sales","marketing","hr","careers","jobs","press","media","team","general"}

def _prompt(name, email, company):
    domain = extract_domain(email)
    personal = is_personal_email(email)
    generic  = is_generic_email(email)
    co       = company or f"infer from domain {domain}"

    return f"""You are a sales intelligence analyst for Buddywise — AI workplace safety using computer vision. Analyse this inbound lead and return JSON only, no markdown.

BUDDYWISE: Detects PPE violations, zone breaches, vehicle hazards, person-down via existing cameras + Buddy Box edge device. Sells to manufacturing, chemical, mining, logistics, construction, energy companies with 200+ workers on physical sites. Active in DACH, Nordics, UK, Poland.

LEAD: Name={name} | Email={email} | Domain={domain} | Company={co} | PersonalEmail={personal} | GenericEmail={generic}

SCORING:
Company(0-100): Industry(0-40: chemical/mining/heavy-mfg/oil-gas=38-40, food-mfg/pharma/construction/logistics=27-35, healthcare/retail-warehouse=16-25, restaurants/retail/media=6-15, software/finance/consulting=0-5) + Size(0-25: 50k+=25,10-50k=22,1-10k=18,200-1k=12,50-200=5,<50=0) + Geography(0-20: DACH=20,Nordics=19,UK/Benelux=16,CoreEU=14,RestEU=11,Americas=8,Other=4) + PhysicalRisk(0-15: multi-hazardous=15,factories=12,mixed=8,office=2)
FitLabel: 80-100=STRONG FIT, 60-79=GOOD FIT, 40-59=POSSIBLE FIT, 20-39=WEAK FIT, 0-19=NOT A FIT

Person(0-100): Authority(0-50: EHSManager/SafetyMgr/PlantMgr=50,OpsManager/ProcurementMgr=45,COO/VPOps=40,CEO/MD=35,CFO=30,HRDir=22,SustainabilityDir=20,ITMgr=12,Marketing=5,Unknown=10) + Seniority(0-30: C-Suite=28,VP=24,Director=20,SrMgr=15,Mgr=12,Individual=5) + Signal(0-20: operational-buyer-inbound=20,procurement-inbound=18,c-suite-inbound=15,influencer=12,cold=8)
Tier: 65+=DECISION_MAKER, 40-64=INFLUENTIAL, <40=CONNECTOR

BuyingSignals: CRITICAL+25(new leader<18mo, recent accident, new site expansion, safety hiring, procurement inbound) HIGH+15(ESG safety targets, peer accident, regulatory audit, M&A, Industry4.0) MEDIUM+8(rapid growth, cost reduction, Atlas Copco/Ramudden connection)
SignalLabel: 60+=HOT, 35-59=WARM, 10-34=LUKEWARM, 0-9=COLD

Priority: FAST_TRACK=Company>=80 AND Person>=65 | PURSUE=Company>=50 OR Person>=65 | NURTURE=Company<40 AND Person>=65 | DEPRIORITISE=both low

Return ONLY this JSON:
{{"company":{{"name":"","industry":"","industry_tier":"","size_employees":"","revenue_estimate":"","headquarters":"","countries_operating":[],"physical_operations":"","known_hazards":[],"buddywise_relevant_features":[],"fit_score":0,"fit_label":"","fit_reasoning":"","score_breakdown":{{"industry_fit":0,"company_size":0,"geography":0,"physical_site_risk":0}}}},"person":{{"name":"{name}","likely_role":"","department":"","seniority_level":"","decision_authority":"","budget_relevance":"","person_score":0,"person_tier":"","tier_reasoning":"","key_insight":"","score_breakdown":{{"decision_authority":0,"seniority":0,"engagement_signal":0}}}},"buying_signals":[{{"signal_name":"","strength":"","score":0,"evidence":""}}],"buying_signal_total":0,"buying_signal_label":"","sales_action":{{"priority":"","priority_reasoning":"","subject_line":"","opening_angle":"","next_step":"","next_step_text":"","critical_caution":""}},"confidence":{{"company_confidence":"","person_confidence":"","overall_confidence":"","data_notes":"","is_personal_email":{str(personal).lower()},"is_generic_email":{str(generic).lower()}}}}}"""

def _parse(text):
    if "```" in text:
        text = re.sub(r"```(?:json)?\n?","",text).replace("```","").strip()
    s,e = text.find("{"), text.rfind("}")+1
    if s!=-1 and e>s: text=text[s:e]
    return json.loads(text)

def analyse_lead_claude(api_key, name, email, company=None):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2000, temperature=0,
        messages=[{"role":"user","content":_prompt(name,email,company)}]
    )
    return _parse(msg.content[0].text.strip())

def analyse_lead_gemini(api_key, name, email, company=None):
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-1.5-flash", contents=_prompt(name,email,company))
    return _parse(response.text.strip())

def analyse_lead(api_key, name, email, company=None, provider="claude"):
    return analyse_lead_gemini(api_key,name,email,company) if provider=="gemini" else analyse_lead_claude(api_key,name,email,company)
