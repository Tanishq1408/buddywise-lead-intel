"""Buddywise Lead Intelligence Platform — Fixed Version"""

import streamlit as st, time
from intelligence import analyse_lead, extract_domain, is_personal_email, is_generic_email
from buddywise_context import CASE_STUDY_LEADS, SHOWCASE_LEADS, SAMPLE_LEADS, PRIORITY_MATRIX, PERSON_TIERS

st.set_page_config(page_title="Buddywise Lead Intel", page_icon="🦺", layout="wide")

st.markdown("""<style>
.block-container{padding:1.2rem 2rem 2rem;max-width:1400px}
.priority-banner{border-radius:12px;padding:18px 22px;margin-bottom:1.2rem;border-left:5px solid}
.intel-card{background:#111827;border:1px solid #1F2937;border-radius:12px;padding:18px;margin-bottom:.8rem}
.card-header{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:#6B7280;border-bottom:1px solid #1F2937;padding-bottom:7px;margin-bottom:10px}
.big-name{font-size:1.2rem;font-weight:700;color:#F9FAFB;margin:0 0 3px}
.meta{font-size:.8rem;color:#9CA3AF;margin-bottom:10px}
.tag{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.7rem;font-weight:600;margin:2px 2px 2px 0}
.detail{font-size:.82rem;color:#D1D5DB;margin:4px 0;display:flex;align-items:flex-start;gap:5px}
.hbox{background:#1F2937;border-radius:8px;padding:9px 12px;margin:8px 0;font-size:.82rem;color:#D1D5DB;border-left:3px solid}
.sig{background:#111827;border:1px solid #1F2937;border-radius:8px;padding:10px 12px;margin:5px 0}
.sig-name{font-size:.83rem;font-weight:600;color:#F9FAFB;margin:0 0 2px}
.sig-ev{font-size:.76rem;color:#9CA3AF;margin:0}
.action-card{background:#111827;border:1px solid #1F2937;border-radius:12px;padding:18px 22px;margin-top:.8rem}
.code-box{background:#0D1117;border:1px solid #374151;border-radius:8px;padding:9px 12px;font-family:monospace;font-size:.83rem;color:#34D399;margin:6px 0;word-break:break-all}
.caution{background:#1C1007;border:1px solid #78350F;border-radius:6px;padding:6px 10px;font-size:.78rem;color:#FCD34D;margin:3px 0}
.empty{background:#111827;border:1px dashed #374151;border-radius:12px;padding:40px 30px;text-align:center;margin:1.5rem 0}
div[data-testid="stButton"]>button{background:#2563EB;color:#fff;border:none;border-radius:8px;font-weight:600}
div[data-testid="stButton"]>button:hover{background:#1D4ED8;color:#fff}
div[data-testid="metric-container"]{background:#111827;border:1px solid #1F2937;border-radius:10px;padding:12px 16px}
</style>""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def pc(p): return PRIORITY_MATRIX.get(p, PRIORITY_MATRIX["QUALIFY"])
def sig_emoji(s): return {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡"}.get(s,"⚪")
def sig_col(s): return {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308"}.get(s,"#6B7280")
def tier_col(t): return PERSON_TIERS.get(t, {}).get("color", "#6B7280")
def tier_label(t): return PERSON_TIERS.get(t, {}).get("label", t.replace("_"," ").title())
def tier_desc(t): return PERSON_TIERS.get(t, {}).get("description", "")
def fit_col(l): return {"STRONG FIT":"#059669","GOOD FIT":"#3B82F6","POSSIBLE FIT":"#D97706","WEAK FIT":"#F97316","NOT A FIT":"#EF4444"}.get(l,"#6B7280")
def sl_col(l): return {"HOT":"#EF4444","WARM":"#F97316","LUKEWARM":"#EAB308","COLD":"#6B7280"}.get(l,"#6B7280")
def sl_emoji(l): return {"HOT":"🔥 HOT","WARM":"🌡️ WARM","LUKEWARM":"❄️ LUKEWARM","COLD":"🧊 COLD"}.get(l,l)
def conf_col(c): return {"HIGH":"#059669","MEDIUM":"#D97706","LOW":"#EF4444","UNKNOWN":"#6B7280"}.get(c,"#6B7280")

def get_api_key():
    try: return st.secrets["ANTHROPIC_API_KEY"]
    except: return st.session_state.get("api_key","")

def get_gemini_key():
    try: return st.secrets["GOOGLE_API_KEY"]
    except: return st.session_state.get("gemini_key","")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦺 Buddywise Lead Intel")
    st.markdown("---")

    # Provider selection
    provider = st.radio("AI Provider", ["Claude (Anthropic)","Gemini (Google — Free)"], index=0)
    use_gemini = "Gemini" in provider

    # API key input
    try:
        _ = st.secrets["ANTHROPIC_API_KEY"] if not use_gemini else st.secrets["GOOGLE_API_KEY"]
    except:
        if use_gemini:
            st.markdown("**🔑 Google API Key**")
            gkey = st.text_input("Google AI Key", type="password", placeholder="AIza...")
            if gkey: st.session_state["gemini_key"] = gkey
            st.markdown("[Get free key →](https://aistudio.google.com/apikey)", unsafe_allow_html=True)
        else:
            st.markdown("**🔑 Anthropic API Key**")
            akey = st.text_input("Anthropic Key", type="password", placeholder="sk-ant-...")
            if akey: st.session_state["api_key"] = akey
            st.markdown("[Get key →](https://console.anthropic.com)", unsafe_allow_html=True)

    st.markdown("---")

    # Lead selector — reliable selectbox approach
    st.markdown("**📋 Select a Lead**")
    all_options = ["— type manually —"] + [
        f"{l['name']} · {l['company']}" for l in SAMPLE_LEADS
    ]
    chosen = st.selectbox("Quick-fill", all_options, key="lead_selector", label_visibility="collapsed")

    # Copy-paste reference table
    with st.expander("📋 Copy-paste table", expanded=False):
        import pandas as pd
        df = pd.DataFrame([
            {"Name": l["name"], "Email": l["email"], "Company": l["company"]}
            for l in SAMPLE_LEADS
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption("Built by Tanishq Singh\nMSc PM & Data Science · HTW Berlin\nBuddywise Case Study · July 2025")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;padding-bottom:1.2rem;border-bottom:1px solid #1F2937;margin-bottom:1.2rem">
  <span style="font-size:2rem">🦺</span>
  <div>
    <p style="font-size:1.4rem;font-weight:700;color:#F9FAFB;margin:0">Buddywise Lead Intelligence</p>
    <p style="font-size:.8rem;color:#6B7280;margin:0">AI-powered sales qualification · paste an email, get a decision</p>
  </div>
</div>""", unsafe_allow_html=True)

# ── INPUT FORM ────────────────────────────────────────────────────────────────
# Resolve selected lead
_selected_lead = {}
chosen_key = st.session_state.get("lead_selector", "— type manually —")
if chosen_key and chosen_key != "— type manually —":
    for _l in SAMPLE_LEADS:
        if f"{_l['name']} · {_l['company']}" == chosen_key:
            _selected_lead = _l
            break

c1, c2, c3, c4 = st.columns([2.5, 2.5, 2, 1])
with c1: name    = st.text_input("Full Name",          value=_selected_lead.get("name",""),    placeholder="e.g. Markus Kamieth")
with c2: email   = st.text_input("Email Address",      value=_selected_lead.get("email",""),   placeholder="e.g. markus.kamieth@basf.com")
with c3: company = st.text_input("Company (optional)", value=_selected_lead.get("company",""), placeholder="Auto-detected from email")
with c4:
    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
    analyse_btn = st.button("🔍 Analyse", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── EMAIL FLAGS (non-blocking) ────────────────────────────────────────────────
if email and "@" in email:
    if is_personal_email(email):
        st.warning("📧 Personal email — company association unclear. Tool will still analyse with lower confidence.")
    elif is_generic_email(email):
        st.warning("📬 Generic routing email — this may not be a personal contact. Tool will still analyse.")

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if analyse_btn:
    # Validation — only block truly invalid emails
    if not name.strip():
        st.error("Please enter a name."); st.stop()
    if not email.strip() or "@" not in email or "." not in email.split("@")[-1]:
        st.error("Please enter a valid email address (must contain @ and a domain)."); st.stop()

    api_key = get_gemini_key() if use_gemini else get_api_key()
    if not api_key:
        st.error(f"No API key found. Enter your {'Google' if use_gemini else 'Anthropic'} key in the sidebar.")
        st.stop()

    with st.spinner("🔍 Analysing lead..."):
        try:
            t0 = time.time()
            result = analyse_lead(
                api_key=api_key,
                name=name.strip(),
                email=email.strip(),
                company=company.strip() or None,
                provider="gemini" if use_gemini else "claude"
            )
            elapsed = round(time.time()-t0, 1)
        except Exception as e:
            err = str(e)
            if "credit balance" in err or "insufficient" in err.lower():
                st.error("💳 Claude API credits exhausted. Options:")
                st.info("1. Add credits at console.anthropic.com → Billing (minimum $5)\n2. Switch to **Gemini (Google — Free)** in the sidebar — select it and enter your Google AI key from aistudio.google.com/apikey")
            elif "quota" in err.lower() or "rate" in err.lower():
                st.error("⏱️ API rate limit hit. Wait 30 seconds and try again.")
            elif "invalid" in err.lower() and "key" in err.lower():
                st.error("🔑 Invalid API key. Check your key in the sidebar.")
            else:
                st.error(f"Analysis failed: {err}")
            st.stop()

    # ── DATA EXTRACTION ────────────────────────────────────────────────────────
    co  = result.get("company", {})
    pe  = result.get("person", {})
    sigs = result.get("buying_signals", [])
    sig_total = result.get("buying_signal_total", 0)
    sig_label = result.get("buying_signal_label", "COLD")
    act = result.get("sales_action", {})
    conf = result.get("confidence", {})
    priority = act.get("priority", "QUALIFY")
    cfg = pc(priority)
    co_score = co.get("fit_score", 0)
    pe_score = pe.get("person_score", 0)
    fit_label = co.get("fit_label", "UNKNOWN")
    pe_tier   = pe.get("person_tier", "UNKNOWN")
    hx = cfg["hex_color"]
    bg = cfg["bg_hex"]

    # ── PRIORITY BANNER ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="priority-banner" style="background:{bg};border-left-color:{hx};border:1px solid {hx}33">
      <p style="font-size:1.5rem;font-weight:800;color:{hx};margin:0">{cfg['emoji']} {cfg['label']}</p>
      <p style="font-size:.88rem;color:#D1D5DB;margin:3px 0 0">{cfg['action']}</p>
      <p style="font-size:.75rem;font-weight:600;color:{hx};margin:5px 0 0;text-transform:uppercase;letter-spacing:.8px">⏱ {cfg['sla']}</p>
    </div>""", unsafe_allow_html=True)

    # Metrics
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Company Fit",    f"{co_score}/100", fit_label)
    m2.metric("Person Score",   f"{pe_score}/100", tier_label(pe_tier))
    m3.metric("Buying Signals", f"{sig_total}/100", sl_emoji(sig_label))
    m4.metric("Confidence",     conf.get("overall_confidence","—"), f"Analysed in {elapsed}s")

    st.markdown("<div style='margin:.8rem 0'></div>", unsafe_allow_html=True)

    # ── THREE COLUMNS ──────────────────────────────────────────────────────────
    colA, colB, colC = st.columns(3)

    # COMPANY
    with colA:
        fc = fit_col(fit_label)
        st.markdown(f"""
        <div class="intel-card">
          <div class="card-header">🏭 Company Intelligence</div>
          <p class="big-name">{co.get('name','Unknown')}</p>
          <p class="meta">{co.get('industry','—')} · {co.get('headquarters','—')}</p>
          <span class="tag" style="background:{fc}22;color:{fc};border:1px solid {fc}44">{fit_label}</span>
          <span class="tag" style="background:#1F2937;color:#9CA3AF">{co.get('industry_tier','—')}</span>
        </div>""", unsafe_allow_html=True)

        st.progress(min(co_score/100,1.0))

        with st.expander("Score breakdown"):
            bd = co.get("score_breakdown",{})
            for k,lbl,mx in [("industry_fit","Industry (max 40)",40),("company_size","Size (max 25)",25),("geography","Geography (max 20)",20),("physical_site_risk","Physical Risk (max 15)",15)]:
                v = bd.get(k,0)
                c_,c2_ = st.columns([3,1])
                c_.caption(lbl); c_.progress(v/mx if mx else 0)
                c2_.markdown(f"<p style='color:#F9FAFB;font-weight:700;margin-top:18px;font-size:.9rem'>{v}</p>",unsafe_allow_html=True)

        for icon,txt in [("👥",f"Employees: {co.get('size_employees','—')}"),("💰",f"Revenue: {co.get('revenue_estimate','—')}"),("🌍",f"Markets: {', '.join(co.get('countries_operating',[])[:3])}")]:
            st.markdown(f"<div class='detail'><span>{icon}</span><span>{txt}</span></div>",unsafe_allow_html=True)

        haz = co.get("known_hazards",[])
        if haz:
            st.markdown("**Safety Hazards**")
            for h in haz[:3]: st.markdown(f"<div class='detail'><span style='color:#EF4444'>⚠</span><span>{h}</span></div>",unsafe_allow_html=True)

        feats = co.get("buddywise_relevant_features",[])
        if feats:
            st.markdown("**Buddywise Features**")
            for f in feats[:3]: st.markdown(f"<div class='detail'><span style='color:#3B82F6'>✓</span><span>{f}</span></div>",unsafe_allow_html=True)

        if co.get("fit_reasoning"):
            st.markdown(f"<div class='hbox' style='border-left-color:{fc}'>💡 {co['fit_reasoning']}</div>",unsafe_allow_html=True)

    # PERSON
    with colB:
        tc = tier_col(pe_tier)
        pt_label = tier_label(pe_tier)
        pt_desc  = tier_desc(pe_tier)
        st.markdown(f"""
        <div class="intel-card">
          <div class="card-header">👤 Person Intelligence</div>
          <p class="big-name">{pe.get('name',name)}</p>
          <p class="meta">{pe.get('likely_role','—')}</p>
          <span class="tag" style="background:{tc}22;color:{tc};border:1px solid {tc}44">{pt_label}</span>
          <span class="tag" style="background:#1F2937;color:#9CA3AF">{pe.get('seniority_level','—').replace('_','-')}</span>
          <p style="font-size:.76rem;color:#6B7280;margin:8px 0 0">{pt_desc}</p>
        </div>""", unsafe_allow_html=True)

        st.progress(min(pe_score/100,1.0))

        with st.expander("Score breakdown"):
            bd = pe.get("score_breakdown",{})
            for k,lbl,mx in [("decision_authority","Authority (max 50)",50),("seniority","Seniority (max 30)",30),("engagement_signal","Signal (max 20)",20)]:
                v = bd.get(k,0)
                c_,c2_ = st.columns([3,1])
                c_.caption(lbl); c_.progress(v/mx if mx else 0)
                c2_.markdown(f"<p style='color:#F9FAFB;font-weight:700;margin-top:18px;font-size:.9rem'>{v}</p>",unsafe_allow_html=True)

        for icon,txt in [("🏢",f"Dept: {pe.get('department','—')}"),("💼",f"Authority: {pe.get('decision_authority','—')}"),("💰",f"Budget: {pe.get('budget_relevance','—')}"),("🎯",f"EHS Relevant: {'Yes ✓' if pe.get('is_ehs_relevant') else 'No ✗'}")]:
            st.markdown(f"<div class='detail'><span>{icon}</span><span>{txt}</span></div>",unsafe_allow_html=True)

        if pe.get("tier_reasoning"):
            st.markdown(f"<div class='hbox' style='border-left-color:{tc}'>{pe['tier_reasoning']}</div>",unsafe_allow_html=True)
        if pe.get("key_insight"):
            st.markdown(f"<div class='hbox' style='border-left-color:#8B5CF6'>💡 {pe['key_insight']}</div>",unsafe_allow_html=True)

    # SIGNALS
    with colC:
        slc = sl_col(sig_label)
        st.markdown(f"""
        <div class="intel-card">
          <div class="card-header">📡 Buying Signals</div>
          <p class="big-name" style="color:{slc}">{sl_emoji(sig_label)}</p>
          <p class="meta">Signal Score: {sig_total}/100</p>
        </div>""", unsafe_allow_html=True)

        st.progress(min(sig_total/100,1.0))

        if sigs:
            st.markdown("**Detected Signals**")
            for sig in sigs:
                sc_ = sig_col(sig.get("strength","MEDIUM"))
                st.markdown(f"""
                <div class="sig" style="border-left:3px solid {sc_}">
                  <p class="sig-name">{sig_emoji(sig.get('strength',''))} {sig.get('signal_name','—')} <span style="float:right;font-size:.73rem;color:{sc_}">+{sig.get('score',0)} pts</span></p>
                  <p class="sig-ev">{sig.get('evidence','—')}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="sig"><p class="sig-name">🧊 No signals detected</p><p class="sig-ev">Standard sales cycle expected.</p></div>',unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Data Confidence**")
        for lbl,key in [("Company","company_confidence"),("Person","person_confidence")]:
            cv = conf.get(key,"UNKNOWN")
            cc = conf_col(cv)
            st.markdown(f"<div class='detail'><span style='width:80px'>{lbl}:</span><span style='color:{cc};font-weight:600'>{cv}</span></div>",unsafe_allow_html=True)
        if conf.get("data_notes"): st.caption(conf["data_notes"])
        if conf.get("is_personal_email"): st.caption("⚠️ Personal email — lower person confidence")
        if conf.get("is_generic_email"):  st.caption("⚠️ Generic email — may not be a direct contact")

    # ── SALES ACTION — MINIMAL ─────────────────────────────────────────────────
    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

    subj    = act.get("subject_line","—")
    angle   = act.get("opening_angle","—")
    ns_type = act.get("next_step","—").replace("_"," ")
    ns_text = act.get("next_step_text","")
    caution = act.get("critical_caution","")
    p_why   = act.get("priority_reasoning","")

    sa1, sa2 = st.columns([1, 1])

    with sa1:
        st.markdown("""<div class="intel-card"><div class="card-header">📧 What to send</div></div>""", unsafe_allow_html=True)
        st.markdown("**Subject line**")
        st.code(subj, language=None)
        st.markdown("**Opening angle**")
        st.markdown(f"<div class='detail'>{angle}</div>", unsafe_allow_html=True)

    with sa2:
        st.markdown("""<div class="intel-card"><div class="card-header">▶ What to do next</div></div>""", unsafe_allow_html=True)
        ns_color = {"DEMO_REQUEST":"#059669","DISCOVERY_CALL":"#3B82F6","CONTENT_SEND":"#D97706","LINKEDIN_CONNECT":"#8B5CF6","FIND_CHAMPION":"#F97316"}.get(act.get("next_step",""), "#6B7280")
        st.markdown(f"<div style='background:{ns_color}22;border:1px solid {ns_color}44;border-radius:8px;padding:10px 14px;margin-bottom:8px'><p style='color:{ns_color};font-weight:700;font-size:.9rem;margin:0'>{ns_type}</p><p style='color:#D1D5DB;font-size:.82rem;margin:4px 0 0'>{ns_text}</p></div>", unsafe_allow_html=True)
        if p_why:
            st.markdown(f"<div class='detail' style='color:#9CA3AF'><span>💡</span><span>{p_why}</span></div>", unsafe_allow_html=True)
        if caution:
            st.markdown(f'<div class="caution" style="margin-top:8px">⚡ {caution}</div>', unsafe_allow_html=True)

    with st.expander("🔧 Raw JSON"): st.json(result)

else:
    st.markdown("""
    <div class="empty">
      <p style="font-size:2.2rem;margin:0">🦺</p>
      <p style="font-size:1.05rem;font-weight:600;color:#F9FAFB;margin:10px 0 3px">Paste an inbound email. Get a decision.</p>
      <p style="font-size:.83rem;color:#6B7280;margin:0">Enter a name and email above, or click any lead in the sidebar.</p>
    </div>""", unsafe_allow_html=True)
