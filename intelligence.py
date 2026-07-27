"""
Buddywise Lead Intelligence — API Layer
Supports: Anthropic Claude + Google Gemini (free)
"""
import os
import json
import re
import streamlit as st
from google import genai
from google.genai.errors import APIError
from buddywise_context import BUDDYWISE_DESCRIPTION


def extract_domain(email):
    return email.strip().split("@")[1].lower() if "@" in email else email.strip()


def is_personal_email(email):
    personal = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
        "me.com", "gmx.com", "gmx.de", "web.de", "proton.me", "protonmail.com", "aol.com"
    }
    return extract_domain(email) in personal


def is_generic_email(email):
    generic = {
        "info", "contact", "hello", "office", "admin", "support", "sales",
        "marketing", "hr", "careers", "jobs", "press", "media", "team", "general"
    }
    return email.split("@")[0].lower() in generic


def _system_prompt():
    return f"""You are a sales intelligence analyst for Buddywise — AI-powered workplace safety.

{BUDDYWISE_DESCRIPTION}

SCORING RULES:
COMPANY FIT (0-100): Industry(0-40) + Size(0-25) + Geography(0-20) + Physical Risk(0-15)
  Industry tiers: Chemical/Mining/Heavy Mfg/Oil&Gas/Pulp&Paper(36-40) | Food Mfg/Pharma Mfg/Construction/Logistics(26-35) | Healthcare/General Logistics(16-25) | Restaurants/Retail/Media(6-15) | Software/Finance/Consulting(0-5)
  Size: 50k+→25, 10-50k→22, 1-10k→18, 200-1k→12, 50-200→5, <50→0
  Geography: DACH→20, Nordics→19, UK/Benelux→16, Core EU→14, Rest EU→11, N.America→8, Other→4
  Physical risk: Multiple hazardous sites→15, Factories/plants→12, Mixed→8, Office-only→2

PERSON SCORE (0-100): Authority(0-50) + Seniority(0-30) + Signal(0-20)
  CSO/VP EHS/Head Safety→50, COO/VP Ops→47, Plant Manager→44, CEO→42, CFO→35
  Safety Manager→30, Ops Manager→28, HR Director→22, Procurement→15, IT→12, Marketing→5
  C-Suite→30, VP→25, Director→20, Sr Mgr→15, Mgr→10
  C-Suite inbound→20, Procurement inbound→18, Director inbound→14, Cold→8

BUYING SIGNALS: CRITICAL(+25): new leader <18mo, recent accident, new site/expansion, safety hiring, procurement contact
HIGH(+15): ESG report with safety targets, peer accident, regulatory audit, M&A/restructuring, Industry 4.0
MEDIUM(+8): rapid growth, cost reduction program, Atlas Copco/Ramudden connection

PRIORITY: FAST_TRACK→Company≥80 AND Person≥70 | PURSUE→Company≥65 AND Person≥50 | QUALIFY→Company≥40 | NURTURE→Company<40 AND Person≥70 | DEPRIORITISE→both low

Return ONLY valid JSON. No markdown, no explanation."""


def _user_prompt(name, email, company):
    domain = extract_domain(email)
    personal = is_personal_email(email)
    generic = is_generic_email(email)
    co = company or f"Infer from domain: {domain}"
    return f"""Analyse this inbound lead for Buddywise:
Name: {name} | Email: {email} | Domain: {domain} | Company: {co}
Personal email: {personal} | Generic email: {generic}

Return this exact JSON:
{{"company":{{"name":"","industry":"","industry_tier":"TIER_1|TIER_2|TIER_3|TIER_4|TIER_5","size_employees":"","revenue_estimate":"","headquarters":"","countries_operating":[],"physical_operations":"","known_hazards":[],"buddywise_relevant_features":[],"fit_score":0,"fit_label":"STRONG FIT|GOOD FIT|POSSIBLE FIT|WEAK FIT|NOT A FIT","fit_reasoning":"","score_breakdown":{{"industry_fit":0,"company_size":0,"geography":0,"physical_site_risk":0}}}},"person":{{"name":"{name}","likely_role":"","department":"","seniority_level":"C_SUITE|VP|DIRECTOR|SENIOR_MANAGER|MANAGER|INDIVIDUAL|UNKNOWN","decision_authority":"","is_ehs_relevant":true,"budget_relevance":"HIGH|MEDIUM|LOW|UNKNOWN","person_score":0,"person_tier":"CHAMPION|INFLUENCER|GATEKEEPER|UNKNOWN","tier_reasoning":"","key_insight":"","score_breakdown":{{"decision_authority":0,"seniority":0,"engagement_signal":0}}}},"buying_signals":[{{"signal_name":"","strength":"CRITICAL|HIGH|MEDIUM","score":25,"evidence":""}}],"buying_signal_total":0,"buying_signal_label":"HOT|WARM|LUKEWARM|COLD","sales_action":{{"priority":"FAST_TRACK|PURSUE|QUALIFY|NURTURE|DEPRIORITISE","priority_reasoning":"","suggested_subject_line":"","opening_angle":"","specific_hook":"","suggested_next_step":"DEMO_REQUEST|DISCOVERY_CALL|CONTENT_SEND|LINKEDIN_CONNECT|SENIOR_BDR_ESCALATE","next_step_detail":"","caution_flags":[],"ideal_contact_strategy":""}},"confidence":{{"company_confidence":"HIGH|MEDIUM|LOW|UNKNOWN","person_confidence":"HIGH|MEDIUM|LOW|UNKNOWN","overall_confidence":"HIGH|MEDIUM|LOW|UNKNOWN","data_notes":"","is_personal_email":{str(personal).lower()},"is_generic_email":{str(generic).lower()},"recommendation_note":""}}}}"""


def _parse(text):
    if "```" in text:
        text = re.sub(r"```(?:json)?\n?", "", text)
        text = re.sub(r"```", "", text).strip()
    s, e = text.find("{"), text.rfind("}") + 1
    if s != -1 and e > s:
        text = text[s:e]
    return json.loads(text)


def analyse_lead_claude(api_key, name, email, company=None):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2500,
        temperature=0,
        system=_system_prompt(),
        messages=[{"role": "user", "content": _user_prompt(name, email, company)}],
    )
    return _parse(msg.content[0].text.strip())


def analyse_lead_gemini(api_key, name, email, company=None):
    # Determine key from parameter, Streamlit secrets, or environment variable
    effective_key = api_key or st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not effective_key:
        raise ValueError("Missing Gemini API key. Please check your secrets or input parameters.")

    client = genai.Client(api_key=effective_key)
    prompt = _system_prompt() + "\n\n" + _user_prompt(name, email, company)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return _parse(response.text.strip())
    except APIError as e:
        if "429" in str(e):
            st.warning("⚠️ Free API quota limit reached. Please wait 30–60 seconds before submitting another request.")
            raise e
        else:
            st.error(f"Gemini API Error: {e}")
            raise e


def analyse_lead(api_key, name, email, company=None, provider="claude"):
    if provider == "gemini":
        return analyse_lead_gemini(api_key, name, email, company)
    return analyse_lead_claude(api_key, name, email, company)
