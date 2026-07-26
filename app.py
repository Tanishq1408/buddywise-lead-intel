"""
Buddywise Lead Intelligence Platform
AI-powered sales qualification — built for the Buddywise case study
Author: Tanishq Singh
"""

import streamlit as st
import time
import json
from intelligence import analyse_lead, extract_domain, is_personal_email, is_generic_email
from buddywise_context import SAMPLE_LEADS, PRIORITY_MATRIX

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Buddywise Lead Intel",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.block-container {
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1400px;
}

/* ── HEADER ── */
.bw-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 0 1.5rem 0;
    border-bottom: 1px solid #1F2937;
    margin-bottom: 1.5rem;
}
.bw-logo {
    font-size: 2rem;
}
.bw-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #F9FAFB;
    margin: 0;
    line-height: 1.2;
}
.bw-subtitle {
    font-size: 0.82rem;
    color: #6B7280;
    margin: 2px 0 0 0;
}

/* ── PRIORITY BANNER ── */
.priority-banner {
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 1.5rem;
    border-left: 5px solid;
}
.priority-label {
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin: 0;
}
.priority-action {
    font-size: 0.9rem;
    margin: 4px 0 0 0;
    opacity: 0.85;
}
.priority-sla {
    font-size: 0.78rem;
    font-weight: 600;
    opacity: 0.7;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── CARDS ── */
.intel-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    margin-bottom: 1rem;
}
.intel-card-header {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #6B7280;
    margin-bottom: 10px;
    border-bottom: 1px solid #1F2937;
    padding-bottom: 8px;
}
.company-name {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F9FAFB;
    margin: 0 0 4px 0;
}
.company-meta {
    font-size: 0.82rem;
    color: #9CA3AF;
    margin-bottom: 14px;
}
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 2px 3px 2px 0;
}
.score-label {
    font-size: 0.78rem;
    color: #9CA3AF;
    margin: 10px 0 3px 0;
}
.score-number {
    font-size: 1.4rem;
    font-weight: 800;
    margin: 0;
}
.detail-item {
    font-size: 0.83rem;
    color: #D1D5DB;
    margin: 5px 0;
    display: flex;
    align-items: flex-start;
    gap: 6px;
}
.detail-bullet {
    color: #4B5563;
    flex-shrink: 0;
    margin-top: 1px;
}
.section-divider {
    border: none;
    border-top: 1px solid #1F2937;
    margin: 12px 0;
}
.highlight-box {
    background: #1F2937;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 0.83rem;
    color: #D1D5DB;
    border-left: 3px solid;
}
.signal-item {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 6px 0;
}
.signal-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #F9FAFB;
    margin: 0 0 3px 0;
}
.signal-evidence {
    font-size: 0.78rem;
    color: #9CA3AF;
    margin: 0;
}
.action-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 20px 24px;
    margin-top: 1rem;
}
.action-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #6B7280;
    margin-bottom: 14px;
    border-bottom: 1px solid #1F2937;
    padding-bottom: 8px;
}
.subject-line-box {
    background: #0D1117;
    border: 1px solid #374151;
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: #34D399;
    margin: 8px 0;
    word-break: break-all;
}
.caution-item {
    background: #1C1007;
    border: 1px solid #78350F;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 0.8rem;
    color: #FCD34D;
    margin: 4px 0;
}
.confidence-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
    color: #6B7280;
    margin: 6px 0;
}
.input-section {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 1.5rem;
}

/* ── SCORE BREAKDOWN ── */
.breakdown-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    font-size: 0.8rem;
    border-bottom: 1px solid #1F2937;
    margin-bottom: 4px;
}
.breakdown-label { color: #9CA3AF; }
.breakdown-score { color: #F9FAFB; font-weight: 600; }

/* ── SAMPLE LEADS SIDEBAR ── */
.sample-lead {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 6px 0;
    cursor: pointer;
    transition: border-color 0.2s;
}
.sample-lead:hover {
    border-color: #374151;
}
.sample-name { font-size: 0.85rem; font-weight: 600; color: #F9FAFB; }
.sample-company { font-size: 0.75rem; color: #6B7280; }

/* ── STREAMLIT OVERRIDES ── */
div[data-testid="stButton"] > button {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 8px 24px;
    transition: background 0.2s;
}
div[data-testid="stButton"] > button:hover {
    background: #1D4ED8;
    color: white;
}
.stProgress > div > div {
    border-radius: 10px;
}
div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 10px;
    padding: 14px 18px;
}
</style>
""", unsafe_allow_html=True)


# ── HELPER FUNCTIONS ─────────────────────────────────────────────────────────────

def get_priority_config(priority: str) -> dict:
    return PRIORITY_MATRIX.get(priority, PRIORITY_MATRIX["QUALIFY"])


def get_signal_emoji(strength: str) -> str:
    return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(strength, "⚪")


def get_signal_color(strength: str) -> str:
    return {"CRITICAL": "#EF4444", "HIGH": "#F97316", "MEDIUM": "#EAB308"}.get(strength, "#6B7280")


def get_tier_color(tier: str) -> str:
    return {"CHAMPION": "#059669", "INFLUENCER": "#3B82F6", "GATEKEEPER": "#F97316", "UNKNOWN": "#6B7280"}.get(tier, "#6B7280")


def get_fit_color(label: str) -> str:
    return {
        "STRONG FIT": "#059669", "GOOD FIT": "#3B82F6",
        "POSSIBLE FIT": "#D97706", "WEAK FIT": "#F97316", "NOT A FIT": "#EF4444"
    }.get(label, "#6B7280")


def get_signal_label_color(label: str) -> str:
    return {"HOT": "#EF4444", "WARM": "#F97316", "LUKEWARM": "#EAB308", "COLD": "#6B7280"}.get(label, "#6B7280")


def get_signal_emoji_label(label: str) -> str:
    return {"HOT": "🔥 HOT", "WARM": "🌡️ WARM", "LUKEWARM": "❄️ LUKEWARM", "COLD": "🧊 COLD"}.get(label, label)


def get_confidence_color(conf: str) -> str:
    return {"HIGH": "#059669", "MEDIUM": "#D97706", "LOW": "#EF4444", "UNKNOWN": "#6B7280"}.get(conf, "#6B7280")


def score_bar(score: int, max_score: int = 100) -> None:
    st.progress(min(score / max_score, 1.0))


def render_score_breakdown(breakdown: dict, labels: dict) -> None:
    for key, val in breakdown.items():
        label = labels.get(key, key.replace("_", " ").title())
        st.markdown(f"""
        <div class="breakdown-row">
            <span class="breakdown-label">{label}</span>
            <span class="breakdown-score">{val}</span>
        </div>""", unsafe_allow_html=True)


# ── API KEY SETUP ─────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """Get API key from secrets or session state."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return st.session_state.get("api_key", "")


# ── SIDEBAR ──────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🦺 Buddywise Lead Intel")
    st.markdown("---")

    # API Key input if not in secrets
    api_key_from_secrets = ""
    try:
        api_key_from_secrets = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass

    if not api_key_from_secrets:
        st.markdown("**🔑 API Configuration**")
        api_key_input = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Enter your Anthropic API key"
        )
        if api_key_input:
            st.session_state["api_key"] = api_key_input
        st.markdown("---")

    # Sample leads
    st.markdown("**📋 Case Study Leads**")
    st.markdown("<small style='color:#6B7280'>Click to auto-fill the form</small>", unsafe_allow_html=True)
    st.markdown("")

    for lead in SAMPLE_LEADS:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="sample-lead">
                <div class="sample-name">{lead['name'].split()[0]} {lead['name'].split()[-1]}</div>
                <div class="sample-company">{lead['company']}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            if st.button("→", key=f"load_{lead['company']}"):
                st.session_state["prefill_name"] = lead["name"]
                st.session_state["prefill_email"] = lead["email"]
                st.session_state["prefill_company"] = lead["company"]
                st.rerun()

    st.markdown("---")
    st.markdown("**ℹ️ About**")
    st.markdown("<small style='color:#6B7280'>Built by Tanishq Singh<br>MSc PM & Data Science · HTW Berlin<br>Buddywise Case Study — July 2025</small>", unsafe_allow_html=True)


# ── MAIN CONTENT ──────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="bw-header">
    <div class="bw-logo">🦺</div>
    <div>
        <p class="bw-title">Buddywise Lead Intelligence</p>
        <p class="bw-subtitle">AI-powered sales qualification · paste an email, get a decision</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Input form
with st.container():
    col1, col2, col3, col4 = st.columns([2.5, 2.5, 2, 1])

    prefill_name = st.session_state.get("prefill_name", "")
    prefill_email = st.session_state.get("prefill_email", "")
    prefill_company = st.session_state.get("prefill_company", "")

    with col1:
        name = st.text_input(
            "Full Name",
            value=prefill_name,
            placeholder="e.g. Markus Kamieth",
            key="input_name"
        )
    with col2:
        email = st.text_input(
            "Email Address",
            value=prefill_email,
            placeholder="e.g. markus.kamieth@basf.com",
            key="input_email"
        )
    with col3:
        company = st.text_input(
            "Company (optional)",
            value=prefill_company,
            placeholder="Auto-detected from email",
            key="input_company"
        )
    with col4:
        st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
        analyse_btn = st.button("🔍 Analyse", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Clear prefill after use
if prefill_name:
    for key in ["prefill_name", "prefill_email", "prefill_company"]:
        if key in st.session_state:
            del st.session_state[key]


# ── EMAIL FLAGS ──────────────────────────────────────────────────────────────────

if email:
    flags = []
    if is_personal_email(email):
        flags.append("⚠️ Personal email detected — company association unclear")
    if is_generic_email(email):
        flags.append("⚠️ Generic/routing email — this may not be a personal contact")
    for flag in flags:
        st.warning(flag)


# ── ANALYSIS ─────────────────────────────────────────────────────────────────────

if analyse_btn:
    if not name.strip():
        st.error("Please enter a name.")
        st.stop()
    if not email.strip() or "@" not in email:
        st.error("Please enter a valid email address.")
        st.stop()

    api_key = get_api_key()
    if not api_key:
        st.error("No API key found. Please enter your Anthropic API key in the sidebar.")
        st.stop()

    with st.spinner("🔍 Analysing lead intelligence..."):
        try:
            start_time = time.time()
            result = analyse_lead(
                api_key=api_key,
                name=name.strip(),
                email=email.strip(),
                company=company.strip() if company.strip() else None
            )
            elapsed = round(time.time() - start_time, 1)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response. Please try again. ({e})")
            st.stop()
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.stop()

    # ── EXTRACT DATA ───────────────────────────────────────────────────────────
    company_data = result.get("company", {})
    person_data = result.get("person", {})
    signals = result.get("buying_signals", [])
    signal_total = result.get("buying_signal_total", 0)
    signal_label = result.get("buying_signal_label", "COLD")
    action = result.get("sales_action", {})
    confidence = result.get("confidence", {})
    priority = action.get("priority", "QUALIFY")
    pconf = get_priority_config(priority)

    company_score = company_data.get("fit_score", 0)
    person_score = person_data.get("person_score", 0)
    fit_label = company_data.get("fit_label", "UNKNOWN")
    person_tier = person_data.get("person_tier", "UNKNOWN")

    # ── PRIORITY BANNER ────────────────────────────────────────────────────────
    hex_color = pconf["hex_color"]
    bg_hex = pconf["bg_hex"]

    st.markdown(f"""
    <div class="priority-banner" style="background:{bg_hex}; border-left-color:{hex_color}; border-color:{hex_color}33;">
        <p class="priority-label" style="color:{hex_color}">
            {pconf['emoji']} {pconf['label']}
        </p>
        <p class="priority-action" style="color:#D1D5DB">{pconf['action']}</p>
        <p class="priority-sla" style="color:{hex_color}">⏱ Target response: {pconf['sla']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Score summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Company Fit", f"{company_score}/100", fit_label)
    with m2:
        st.metric("Person Score", f"{person_score}/100", person_tier)
    with m3:
        signal_delta = get_signal_emoji_label(signal_label)
        st.metric("Buying Signals", f"{signal_total}/100", signal_delta)
    with m4:
        overall_conf = confidence.get("overall_confidence", "MEDIUM")
        st.metric("Data Confidence", overall_conf, f"Analysed in {elapsed}s")

    st.markdown("<div style='margin: 1.2rem 0;'></div>", unsafe_allow_html=True)

    # ── THREE COLUMNS: COMPANY | PERSON | SIGNALS ───────────────────────────────
    col_c, col_p, col_s = st.columns(3)

    # ── COMPANY CARD ─────────────────────────────────────────────────────────────
    with col_c:
        fit_color = get_fit_color(fit_label)
        st.markdown(f"""
        <div class="intel-card">
            <div class="intel-card-header">🏭 Company Intelligence</div>
            <p class="company-name">{company_data.get('name', 'Unknown')}</p>
            <p class="company-meta">
                {company_data.get('industry', '—')} &nbsp;·&nbsp;
                {company_data.get('headquarters', '—')}
            </p>
            <span class="tag" style="background:{fit_color}22; color:{fit_color}; border:1px solid {fit_color}44">
                {fit_label}
            </span>
            <span class="tag" style="background:#1F2937; color:#9CA3AF">
                {company_data.get('industry_tier', '—')}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Score bar
        st.progress(min(company_score / 100, 1.0))

        # Score breakdown
        with st.expander("Score breakdown", expanded=False):
            breakdown = company_data.get("score_breakdown", {})
            labels = {
                "industry_fit": "Industry Fit (max 40)",
                "company_size": "Company Size (max 25)",
                "geography": "Geography (max 20)",
                "physical_site_risk": "Physical Risk (max 15)"
            }
            for key, lbl in labels.items():
                val = breakdown.get(key, 0)
                max_val = int(lbl.split("max ")[-1].replace(")", "")) if "max" in lbl else 40
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.caption(lbl)
                    st.progress(val / max_val if max_val > 0 else 0)
                with c2:
                    st.markdown(f"<p style='color:#F9FAFB;font-weight:700;font-size:0.9rem;margin-top:20px'>{val}</p>", unsafe_allow_html=True)

        # Key facts
        st.markdown("**Key Facts**")
        facts = [
            ("👥", f"Employees: {company_data.get('size_employees', '—')}"),
            ("💰", f"Revenue: {company_data.get('revenue_estimate', '—')}"),
            ("🌍", f"Markets: {', '.join(company_data.get('countries_operating', [])[:3])}"),
        ]
        for icon, fact in facts:
            st.markdown(f"<div class='detail-item'><span>{icon}</span><span>{fact}</span></div>", unsafe_allow_html=True)

        # Physical operations
        if company_data.get("physical_operations"):
            st.markdown("**Physical Operations**")
            st.markdown(f"<div class='detail-item'><span class='detail-bullet'>•</span><span>{company_data['physical_operations']}</span></div>", unsafe_allow_html=True)

        # Known hazards
        hazards = company_data.get("known_hazards", [])
        if hazards:
            st.markdown("**Safety Hazards (Relevant to Buddywise)**")
            for h in hazards[:4]:
                st.markdown(f"<div class='detail-item'><span style='color:#EF4444'>⚠</span><span>{h}</span></div>", unsafe_allow_html=True)

        # Relevant features
        features = company_data.get("buddywise_relevant_features", [])
        if features:
            st.markdown("**Buddywise Features that Apply**")
            for f in features[:4]:
                st.markdown(f"<div class='detail-item'><span style='color:#3B82F6'>✓</span><span>{f}</span></div>", unsafe_allow_html=True)

        # Fit reasoning
        if company_data.get("fit_reasoning"):
            st.markdown(f"""
            <div class="highlight-box" style="border-left-color:{fit_color}">
                💡 {company_data['fit_reasoning']}
            </div>""", unsafe_allow_html=True)

    # ── PERSON CARD ───────────────────────────────────────────────────────────────
    with col_p:
        tier_color = get_tier_color(person_tier)
        seniority = person_data.get("seniority_level", "UNKNOWN").replace("_", "-")

        st.markdown(f"""
        <div class="intel-card">
            <div class="intel-card-header">👤 Person Intelligence</div>
            <p class="company-name">{person_data.get('name', name)}</p>
            <p class="company-meta">{person_data.get('likely_role', '—')}</p>
            <span class="tag" style="background:{tier_color}22; color:{tier_color}; border:1px solid {tier_color}44">
                {person_tier}
            </span>
            <span class="tag" style="background:#1F2937; color:#9CA3AF">
                {seniority}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Score bar
        st.progress(min(person_score / 100, 1.0))

        # Score breakdown
        with st.expander("Score breakdown", expanded=False):
            breakdown = person_data.get("score_breakdown", {})
            labels = {
                "decision_authority": "Decision Authority (max 50)",
                "seniority": "Seniority (max 30)",
                "engagement_signal": "Engagement Signal (max 20)"
            }
            for key, lbl in labels.items():
                val = breakdown.get(key, 0)
                max_val = int(lbl.split("max ")[-1].replace(")", ""))
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.caption(lbl)
                    st.progress(val / max_val if max_val > 0 else 0)
                with c2:
                    st.markdown(f"<p style='color:#F9FAFB;font-weight:700;font-size:0.9rem;margin-top:20px'>{val}</p>", unsafe_allow_html=True)

        # Person details
        st.markdown("**Profile**")
        details = [
            ("🏢", f"Department: {person_data.get('department', '—')}"),
            ("💼", f"Authority: {person_data.get('decision_authority', '—')}"),
            ("💰", f"Budget Access: {person_data.get('budget_relevance', '—')}"),
            ("🎯", f"EHS Relevant: {'Yes ✓' if person_data.get('is_ehs_relevant') else 'No ✗'}"),
        ]
        for icon, detail in details:
            st.markdown(f"<div class='detail-item'><span>{icon}</span><span>{detail}</span></div>", unsafe_allow_html=True)

        # Tier reasoning
        if person_data.get("tier_reasoning"):
            st.markdown(f"""
            <div class="highlight-box" style="border-left-color:{tier_color}">
                {person_data['tier_reasoning']}
            </div>""", unsafe_allow_html=True)

        # Key insight
        if person_data.get("key_insight"):
            st.markdown("**Key Insight**")
            st.markdown(f"""
            <div class="highlight-box" style="border-left-color:#8B5CF6">
                💡 {person_data['key_insight']}
            </div>""", unsafe_allow_html=True)

    # ── BUYING SIGNALS CARD ───────────────────────────────────────────────────────
    with col_s:
        sig_color = get_signal_label_color(signal_label)
        sig_label_display = get_signal_emoji_label(signal_label)

        st.markdown(f"""
        <div class="intel-card">
            <div class="intel-card-header">📡 Buying Signals</div>
            <p class="company-name" style="color:{sig_color}">{sig_label_display}</p>
            <p class="company-meta">Signal Score: {signal_total}/100</p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(min(signal_total / 100, 1.0))

        if signals:
            st.markdown("**Detected Signals**")
            for sig in signals:
                strength = sig.get("strength", "MEDIUM")
                emoji = get_signal_emoji(strength)
                sig_c = get_signal_color(strength)
                score = sig.get("score", 0)

                st.markdown(f"""
                <div class="signal-item" style="border-left: 3px solid {sig_c}">
                    <p class="signal-name">
                        {emoji} {sig.get('signal_name', '—')}
                        <span style="float:right;font-size:0.75rem;color:{sig_c}">+{score} pts</span>
                    </p>
                    <p class="signal-evidence">{sig.get('evidence', '—')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="signal-item">
                <p class="signal-name">🧊 No signals detected</p>
                <p class="signal-evidence">No immediate buying triggers found. Expect a standard sales cycle.</p>
            </div>
            """, unsafe_allow_html=True)

        # Confidence
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("**Data Confidence**")
        for label, key in [("Company data", "company_confidence"), ("Person data", "person_confidence")]:
            conf_val = confidence.get(key, "UNKNOWN")
            conf_color = get_confidence_color(conf_val)
            st.markdown(f"""
            <div class="confidence-bar">
                <span style="width:110px">{label}:</span>
                <span style="color:{conf_color};font-weight:600">{conf_val}</span>
            </div>""", unsafe_allow_html=True)

        if confidence.get("data_notes"):
            st.caption(confidence["data_notes"])

    # ── SALES ACTION CARD ─────────────────────────────────────────────────────────
    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="action-card">
        <div class="action-title">💡 Sales Action Plan</div>
    </div>
    """, unsafe_allow_html=True)

    ac1, ac2, ac3 = st.columns([2, 2, 2])

    with ac1:
        st.markdown("**📧 Suggested Subject Line**")
        subject = action.get("suggested_subject_line", "—")
        st.markdown(f'<div class="subject-line-box">{subject}</div>', unsafe_allow_html=True)
        st.code(subject, language=None)

        st.markdown("**🎯 Opening Angle**")
        st.markdown(f"<div class='detail-item'>{action.get('opening_angle', '—')}</div>", unsafe_allow_html=True)

    with ac2:
        st.markdown("**🔍 Specific Hook**")
        st.markdown(f"""
        <div class="highlight-box" style="border-left-color:#8B5CF6">
            {action.get('specific_hook', '—')}
        </div>""", unsafe_allow_html=True)

        st.markdown("**📋 Recommended Next Step**")
        next_step = action.get("suggested_next_step", "—").replace("_", " ")
        next_detail = action.get("next_step_detail", "")
        st.markdown(f"<div class='detail-item'><span style='color:#3B82F6'>▶</span> <strong>{next_step}</strong></div>", unsafe_allow_html=True)
        if next_detail:
            st.markdown(f"<div class='detail-item'><span class='detail-bullet'>•</span>{next_detail}</div>", unsafe_allow_html=True)

    with ac3:
        st.markdown("**⚠️ Caution Flags**")
        cautions = action.get("caution_flags", [])
        if cautions:
            for c in cautions:
                st.markdown(f'<div class="caution-item">⚡ {c}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="caution-item" style="background:#064E3B;border-color:#065F46;color:#34D399">✓ No major caution flags</div>', unsafe_allow_html=True)

        st.markdown("**💬 Contact Strategy**")
        st.markdown(f"<div class='detail-item'>{action.get('ideal_contact_strategy', '—')}</div>", unsafe_allow_html=True)

    # Priority reasoning
    if action.get("priority_reasoning"):
        st.markdown(f"""
        <div class="highlight-box" style="border-left-color:{hex_color}; margin-top:1rem">
            <strong>Why {priority.replace('_', ' ')}?</strong><br>
            {action['priority_reasoning']}
        </div>""", unsafe_allow_html=True)

    # Raw JSON expander
    with st.expander("🔧 Raw JSON Output (for debugging)", expanded=False):
        st.json(result)


# ── EMPTY STATE ───────────────────────────────────────────────────────────────────
elif not analyse_btn:
    st.markdown("""
    <div style='
        background: #111827;
        border: 1px dashed #374151;
        border-radius: 12px;
        padding: 48px 32px;
        text-align: center;
        margin: 2rem 0;
    '>
        <p style='font-size: 2.5rem; margin: 0'>🦺</p>
        <p style='font-size: 1.1rem; font-weight: 600; color: #F9FAFB; margin: 12px 0 4px'>
            Paste an inbound email. Get a decision.
        </p>
        <p style='font-size: 0.85rem; color: #6B7280; margin: 0'>
            Enter a name and email address above, or click a sample lead in the sidebar to try it instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)
