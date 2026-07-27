"""Buddywise Lead Intelligence"""

import streamlit as st, time
from intelligence import analyse_lead, extract_domain, is_personal_email, is_generic_email
from buddywise_context import CASE_STUDY_LEADS, SHOWCASE_LEADS, SAMPLE_LEADS, PRIORITY_MATRIX, PERSON_TIERS

st.set_page_config(page_title="Buddywise Lead Intel", page_icon="🦺", layout="wide")

st.markdown("""<style>
.block-container{padding:1.2rem 2rem 2rem;max-width:1400px}
.priority-banner{border-radius:12px;padding:16px 22px;margin-bottom:1rem;border-left:5px solid}
.decision-tile{background:#111827;border:1px solid #1F2937;border-radius:10px;padding:14px 18px;margin-bottom:.8rem}
.tile-label{font-size:.66rem;color:#6B7280;text-transform:uppercase;letter-spacing:1.1px;margin:0 0 6px}
.tile-value{font-size:1.05rem;font-weight:700;margin:0 0 3px}
.tile-sub{font-size:.75rem;color:#9CA3AF;margin:0}
.intel-card{background:#111827;border:1px solid #1F2937;border-radius:12px;padding:18px;height:100%;margin-bottom:.8rem}
.card-header{font-size:.67rem;color:#6B7280;text-transform:uppercase;letter-spacing:1.1px;border-bottom:1px solid #1F2937;padding-bottom:7px;margin-bottom:12px}
.big-name{font-size:1.15rem;font-weight:700;color:#F9FAFB;margin:0 0 3px}
.meta{font-size:.8rem;color:#9CA3AF;margin:0 0 10px}
.tag{display:inline-block;padding:3px 11px;border-radius:20px;font-size:.72rem;font-weight:600;margin:2px 2px 2px 0}
.detail{font-size:.81rem;color:#D1D5DB;margin:4px 0;display:flex;gap:6px;align-items:flex-start}
.hbox{background:#1F2937;border-radius:8px;padding:9px 12px;margin:8px 0;font-size:.81rem;color:#D1D5DB;border-left:3px solid}
.sig-item{background:#111827;border:1px solid #1F2937;border-radius:8px;padding:10px 12px;margin:5px 0}
.sig-name{font-size:.82rem;font-weight:600;color:#F9FAFB;margin:0 0 2px}
.sig-ev{font-size:.75rem;color:#9CA3AF;margin:0}
.action-card{background:#111827;border:1px solid #1F2937;border-radius:12px;padding:18px 22px}
.caution{background:#1C1007;border:1px solid #78350F;border-radius:6px;padding:6px 10px;font-size:.78rem;color:#FCD34D;margin:4px 0}
.empty{background:#111827;border:1px dashed #374151;border-radius:12px;padding:40px;text-align:center}
div[data-testid="stButton"]>button{background:#2563EB;color:#fff;border:none;border-radius:8px;font-weight:600}
div[data-testid="stButton"]>button:hover{background:#1D4ED8;color:#fff}
</style>""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def pc(p): return PRIORITY_MATRIX.get(p, PRIORITY_MATRIX["QUALIFY"])
def tier_color(t):  return PERSON_TIERS.get(t,{}).get("color","#6B7280")
def tier_label(t):  return PERSON_TIERS.get(t,{}).get("label", t.replace("_"," ").title())
def tier_desc(t):   return PERSON_TIERS.get(t,{}).get("description","")
def sig_emoji(s):   return {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡"}.get(s,"⚪")
def sig_col(s):     return {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308"}.get(s,"#6B7280")
def urg_label(l):   return {"HOT":"🔥 HOT","WARM":"🌡️ WARM","LUKEWARM":"❄️ LUKEWARM","COLD":"🧊 COLD"}.get(l, l)
def urg_color(l):   return {"HOT":"#EF4444","WARM":"#F97316","LUKEWARM":"#EAB308","COLD":"#6B7280"}.get(l,"#6B7280")
def conf_color(c):  return {"HIGH":"#059669","MEDIUM":"#D97706","LOW":"#EF4444","UNKNOWN":"#6B7280"}.get(c,"#6B7280")

def fit_decision(label):
    if label in ("STRONG FIT","GOOD FIT"):  return label, "#059669"
    if label == "POSSIBLE FIT":             return "POSSIBLE FIT", "#D97706"
    if label == "WEAK FIT":                 return "WEAK FIT", "#F97316"
    return "NOT A FIT", "#EF4444"

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
    provider = st.radio("AI Provider", ["Claude (Anthropic)","Gemini (Google — Free)"], index=0)
    use_gemini = "Gemini" in provider
    try:
        _ = st.secrets["GOOGLE_API_KEY"] if use_gemini else st.secrets["ANTHROPIC_API_KEY"]
    except:
        if use_gemini:
            st.markdown("**🔑 Google AI Key**")
            gk = st.text_input("Key", type="password", placeholder="AIza...", label_visibility="collapsed")
            if gk: st.session_state["gemini_key"] = gk
            st.markdown("[Get free key →](https://aistudio.google.com/apikey)", unsafe_allow_html=True)
        else:
            st.markdown("**🔑 Anthropic Key**")
            ak = st.text_input("Key", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
            if ak: st.session_state["api_key"] = ak
    st.markdown("---")
    st.markdown("**📋 Select a Lead**")
    all_opts = ["— type manually —"] + [f"{l['name']} · {l['company']}" for l in SAMPLE_LEADS]
    chosen = st.selectbox("Lead", all_opts, key="lead_selector", label_visibility="collapsed")
    with st.expander("📋 Copy-paste table", expanded=False):
        import pandas as pd
        st.dataframe(pd.DataFrame([{"Name":l["name"],"Email":l["email"],"Company":l["company"]} for l in SAMPLE_LEADS]),
                     use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Tanishq Singh · HTW Berlin\nBuddywise Case Study · July 2025")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""<div style="display:flex;align-items:center;gap:10px;padding-bottom:1rem;border-bottom:1px solid #1F2937;margin-bottom:1rem">
  <span style="font-size:1.8rem">🦺</span>
  <div>
    <p style="font-size:1.3rem;font-weight:700;color:#F9FAFB;margin:0">Buddywise Lead Intelligence</p>
    <p style="font-size:.78rem;color:#6B7280;margin:0">Paste an email. Get a decision.</p>
  </div>
</div>""", unsafe_allow_html=True)

# ── FORM ─────────────────────────────────────────────────────────────────────
_lead = {}
_sel = st.session_state.get("lead_selector","— type manually —")
if _sel and _sel != "— type manually —":
    for _l in SAMPLE_LEADS:
        if f"{_l['name']} · {_l['company']}" == _sel:
            _lead = _l; break

c1,c2,c3,c4 = st.columns([2.5,2.5,2,1])
with c1: name    = st.text_input("Full Name",          value=_lead.get("name",""),    placeholder="e.g. Markus Kamieth")
with c2: email   = st.text_input("Email Address",      value=_lead.get("email",""),   placeholder="e.g. m.kamieth@basf.com")
with c3: company = st.text_input("Company (optional)", value=_lead.get("company",""), placeholder="Auto-detected")
with c4:
    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
    go = st.button("🔍 Analyse", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if email and "@" in email:
    if is_personal_email(email):
        st.warning("📧 Personal email — company unclear. Analysing with lower confidence.")
    elif is_generic_email(email):
        st.warning("📬 Generic email — may not be a personal contact.")

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if go:
    if not name.strip(): st.error("Please enter a name."); st.stop()
    if not email.strip() or "@" not in email: st.error("Please enter a valid email."); st.stop()
    api_key = get_gemini_key() if use_gemini else get_api_key()
    if not api_key:
        st.error(f"No API key. Add your {'Google' if use_gemini else 'Anthropic'} key in the sidebar."); st.stop()

    with st.spinner("Analysing lead..."):
        try:
            t0 = time.time()
            r = analyse_lead(api_key, name.strip(), email.strip(), company.strip() or None,
                             provider="gemini" if use_gemini else "claude")
            elapsed = round(time.time()-t0, 1)
        except Exception as e:
            err = str(e)
            if "credit balance" in err or "insufficient" in err.lower():
                st.error("💳 Claude credits exhausted. Add credits at console.anthropic.com → Billing, or switch to Gemini (Free)."); st.stop()
            elif "quota" in err.lower() or "rate" in err.lower():
                st.error("⏱️ Rate limit. Wait 30 seconds and try again."); st.stop()
            else:
                st.error(f"Analysis failed: {err}"); st.stop()

    co   = r.get("company",{})
    pe   = r.get("person",{})
    sigs = r.get("buying_signals",[])
    sig_total = r.get("buying_signal_total", 0)
    sig_lbl   = r.get("buying_signal_label", "COLD")
    act  = r.get("sales_action",{})
    conf = r.get("confidence",{})
    priority  = act.get("priority","QUALIFY")
    cfg = pc(priority)
    hx  = cfg["hex_color"]
    bg  = cfg["bg_hex"]
    co_score  = co.get("fit_score", 0)
    pe_score  = pe.get("person_score", 0)
    fit_label = co.get("fit_label","UNKNOWN")
    pe_tier   = pe.get("person_tier","CONNECTOR")
    is_match  = fit_label not in ("NOT A FIT","WEAK FIT")
    fit_dec, fit_color = fit_decision(fit_label)
    tc  = tier_color(pe_tier)
    tl  = tier_label(pe_tier)
    uc  = urg_color(sig_lbl)
    ov_conf = conf.get("overall_confidence","UNKNOWN")

    # ── PRIORITY BANNER ────────────────────────────────────────────────────────
    st.markdown(f"""<div class="priority-banner" style="background:{bg};border-left-color:{hx};border:1px solid {hx}33">
      <p style="font-size:1.4rem;font-weight:800;color:{hx};margin:0">{cfg['emoji']} {cfg['label']}</p>
      <p style="font-size:.84rem;color:#D1D5DB;margin:3px 0 0">{cfg['action']} &nbsp;·&nbsp;
        <span style="color:{hx};font-weight:600">{cfg['sla']}</span> &nbsp;·&nbsp;
        <span style="color:#6B7280">{co.get('name','—')}</span></p>
    </div>""", unsafe_allow_html=True)

    # ── 4 DECISION TILES ───────────────────────────────────────────────────────
    t1, t2, t3, t4 = st.columns(4)

    with t1:
        st.markdown(f"""<div class="decision-tile">
          <p class="tile-label">🏭 Industry Match</p>
          <p class="tile-value" style="color:{fit_color}">{fit_dec}</p>
          <p class="tile-sub">{co.get('industry','—')}</p>
        </div>""", unsafe_allow_html=True)

    with t2:
        st.markdown(f"""<div class="decision-tile">
          <p class="tile-label">👤 Person Relevance</p>
          <p class="tile-value" style="color:{tc}">{tl}</p>
          <p class="tile-sub">{pe.get('likely_role','—')}</p>
        </div>""", unsafe_allow_html=True)

    with t3:
        st.markdown(f"""<div class="decision-tile">
          <p class="tile-label">⚡ Purchase Timing</p>
          <p class="tile-value" style="color:{uc}">{urg_label(sig_lbl)}</p>
          <p class="tile-sub">{len(sigs)} signal{'s' if len(sigs)!=1 else ''} detected</p>
        </div>""", unsafe_allow_html=True)

    with t4:
        cc = conf_color(ov_conf)
        st.markdown(f"""<div class="decision-tile">
          <p class="tile-label">🎯 Data Confidence</p>
          <p class="tile-value" style="color:{cc}">{ov_conf}</p>
          <p class="tile-sub">Analysed in {elapsed}s</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:.4rem 0'></div>", unsafe_allow_html=True)

    # ── 3 DETAIL CARDS ─────────────────────────────────────────────────────────
    col_co, col_pe, col_urg = st.columns(3)

    # COMPANY CARD
    with col_co:
        st.markdown(f"""<div class="intel-card">
          <div class="card-header">🏭 Company</div>
          <p class="big-name">{co.get('name','Unknown')}</p>
          <p class="meta">{co.get('headquarters','—')}</p>
          <span class="tag" style="background:{fit_color}22;color:{fit_color};border:1px solid {fit_color}44">{fit_dec}</span>
          <span class="tag" style="background:#1F2937;color:#9CA3AF">{co.get('industry_tier','—')}</span>
        </div>""", unsafe_allow_html=True)

        for icon, txt in [("👥", f"Employees: {co.get('size_employees','—')}"),
                          ("💰", f"Revenue: {co.get('revenue_estimate','—')}"),
                          ("🌍", f"HQ: {co.get('headquarters','—')}")]:
            st.markdown(f"<div class='detail'><span>{icon}</span><span>{txt}</span></div>", unsafe_allow_html=True)

        if is_match:
            ops = co.get("physical_operations","")
            if ops:
                st.markdown(f"<div class='hbox' style='border-left-color:{fit_color}'>{ops}</div>", unsafe_allow_html=True)

            hazards = co.get("known_hazards",[])
            if hazards:
                st.markdown("**Relevant hazards**")
                for h in hazards[:3]:
                    st.markdown(f"<div class='detail'><span style='color:#EF4444'>⚠</span><span>{h}</span></div>", unsafe_allow_html=True)

            features = co.get("buddywise_relevant_features",[])
            if features:
                st.markdown("**Buddywise features**")
                for f in features[:3]:
                    st.markdown(f"<div class='detail'><span style='color:#3B82F6'>✓</span><span>{f}</span></div>", unsafe_allow_html=True)

            if co.get("fit_reasoning"):
                st.markdown(f"<div class='hbox' style='border-left-color:{fit_color}'>💡 {co['fit_reasoning']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='hbox' style='border-left-color:#EF4444'>❌ {co.get('fit_reasoning','Does not match Buddywise ICP.')}</div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:.8rem;color:#4B5563;margin-top:8px'>Move on. Don't invest more time here.</p>", unsafe_allow_html=True)

    # PERSON CARD
    with col_pe:
        st.markdown(f"""<div class="intel-card">
          <div class="card-header">👤 Person</div>
          <p class="big-name">{pe.get('name', name)}</p>
          <p class="meta">{pe.get('likely_role','—')}</p>
          <span class="tag" style="background:{tc}22;color:{tc};border:1px solid {tc}44">{tl}</span>
          <span class="tag" style="background:#1F2937;color:#9CA3AF">{pe.get('seniority_level','—').replace('_','-')}</span>
        </div>""", unsafe_allow_html=True)

        if is_match:
            for icon, txt in [("🏢", f"Dept: {pe.get('department','—')}"),
                              ("💰", f"Budget: {pe.get('budget_relevance','—')}")]:
                st.markdown(f"<div class='detail'><span>{icon}</span><span>{txt}</span></div>", unsafe_allow_html=True)

            td = tier_desc(pe_tier)
            if td:
                st.markdown(f"<div class='hbox' style='border-left-color:{tc}'>{td}</div>", unsafe_allow_html=True)

            if pe.get("key_insight"):
                st.markdown(f"<div class='hbox' style='border-left-color:#8B5CF6'>💡 {pe['key_insight']}</div>", unsafe_allow_html=True)

            if pe.get("tier_reasoning"):
                st.markdown(f"<div class='detail' style='color:#6B7280'>{pe['tier_reasoning']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='hbox' style='border-left-color:{tc}'>{tier_desc(pe_tier)}</div>", unsafe_allow_html=True)

    # URGENCY CARD (was: Buying Signals)
    with col_urg:
        st.markdown(f"""<div class="intel-card">
          <div class="card-header">⚡ Purchase Timing</div>
          <p class="big-name" style="color:{uc}">{urg_label(sig_lbl)}</p>
          <p class="meta" style="margin-bottom:10px">{len(sigs)} trigger{'s' if len(sigs)!=1 else ''} detected</p>
        </div>""", unsafe_allow_html=True)

        if sigs:
            for sig in sigs[:4]:
                sc = sig_col(sig.get("strength","MEDIUM"))
                score = sig.get("score",0)
                st.markdown(f"""<div class="sig-item" style="border-left:3px solid {sc}">
                  <p class="sig-name">{sig_emoji(sig.get('strength',''))} {sig.get('signal_name','—')}
                    <span style="float:right;font-size:.72rem;color:{sc}">+{score}</span></p>
                  <p class="sig-ev">{sig.get('evidence','—')}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="sig-item">
              <p class="sig-name">🧊 No active triggers</p>
              <p class="sig-ev">Standard sales cycle. No immediate urgency signals.</p>
            </div>""", unsafe_allow_html=True)

        if not is_match:
            st.markdown("<p style='font-size:.78rem;color:#4B5563;margin-top:8px'>Signals are less relevant — company is not a fit.</p>", unsafe_allow_html=True)

        # Confidence note
        st.markdown("<hr style='border:none;border-top:1px solid #1F2937;margin:10px 0'>", unsafe_allow_html=True)
        co_conf = conf.get("company_confidence","UNKNOWN")
        pe_conf = conf.get("person_confidence","UNKNOWN")
        st.markdown(f"<div class='detail'><span>🏭</span><span style='color:{conf_color(co_conf)}'>{co_conf}</span><span style='color:#4B5563'>company data</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='detail'><span>👤</span><span style='color:{conf_color(pe_conf)}'>{pe_conf}</span><span style='color:#4B5563'>person data</span></div>", unsafe_allow_html=True)
        if conf.get("data_notes"):
            st.caption(conf["data_notes"])

    # ── SALES ACTION ───────────────────────────────────────────────────────────
    if is_match:
        st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)
        subj  = act.get("subject_line","—")
        angle = act.get("opening_angle","—")
        ns_k  = act.get("next_step","DISCOVERY_CALL")
        ns_t  = act.get("next_step_text","")
        caut  = act.get("critical_caution","")

        ns_c = {"DEMO_REQUEST":"#059669","DISCOVERY_CALL":"#3B82F6","CONTENT_SEND":"#D97706",
                "LINKEDIN_CONNECT":"#8B5CF6","FIND_CHAMPION":"#F97316"}.get(ns_k,"#6B7280")

        a1, a2 = st.columns(2)
        with a1:
            st.markdown("""<div class="action-card"><div class="card-header">📧 What to send</div></div>""", unsafe_allow_html=True)
            st.markdown("**Subject line**")
            st.code(subj, language=None)
            st.markdown(f"<p class='detail'>{angle}</p>", unsafe_allow_html=True)

        with a2:
            st.markdown("""<div class="action-card"><div class="card-header">▶ Next step</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:{ns_c}22;border:1px solid {ns_c}44;border-radius:8px;padding:12px 16px;margin-bottom:8px">
              <p style="color:{ns_c};font-weight:700;font-size:.9rem;margin:0">{ns_k.replace('_',' ')}</p>
              <p style="color:#D1D5DB;font-size:.82rem;margin:4px 0 0">{ns_t}</p>
            </div>""", unsafe_allow_html=True)
            if caut:
                st.markdown(f'<div class="caution">⚡ {caut}</div>', unsafe_allow_html=True)
            if act.get("priority_reasoning"):
                st.markdown(f"<div class='detail' style='margin-top:6px;color:#6B7280'><span>💡</span><span>{act['priority_reasoning']}</span></div>", unsafe_allow_html=True)

    # ── SCORES AT THE BOTTOM ───────────────────────────────────────────────────
    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)
    with st.expander("📊 Full scores & breakdown", expanded=False):
        s1, s2, s3 = st.columns(3)
        s1.metric("Company Fit Score",   f"{co_score}/100",   fit_label)
        s2.metric("Person Score",        f"{pe_score}/100",   tl)
        s3.metric("Purchase Timing Score",f"{sig_total}/100", urg_label(sig_lbl))

        st.markdown("---")
        left, right = st.columns(2)
        with left:
            st.markdown("**Company score breakdown**")
            for k,lbl,mx in [("industry_fit","Industry (max 40)",40),("company_size","Size (max 25)",25),
                              ("geography","Geography (max 20)",20),("physical_site_risk","Physical Risk (max 15)",15)]:
                v = co.get("score_breakdown",{}).get(k,0)
                ca, cb = st.columns([4,1])
                ca.caption(lbl); ca.progress(v/mx if mx else 0)
                cb.markdown(f"<p style='font-weight:700;color:#F9FAFB;margin-top:18px'>{v}</p>", unsafe_allow_html=True)

        with right:
            st.markdown("**Person score breakdown**")
            for k,lbl,mx in [("decision_authority","Decision Authority (max 50)",50),
                              ("seniority","Seniority (max 30)",30),
                              ("engagement_signal","Engagement Signal (max 20)",20)]:
                v = pe.get("score_breakdown",{}).get(k,0)
                ca, cb = st.columns([4,1])
                ca.caption(lbl); ca.progress(v/mx if mx else 0)
                cb.markdown(f"<p style='font-weight:700;color:#F9FAFB;margin-top:18px'>{v}</p>", unsafe_allow_html=True)

        with st.expander("Raw JSON", expanded=False):
            st.json(r)

else:
    st.markdown("""<div class="empty">
      <p style="font-size:2rem;margin:0">🦺</p>
      <p style="font-size:1rem;font-weight:600;color:#F9FAFB;margin:8px 0 3px">Paste an inbound email. Get a decision.</p>
      <p style="font-size:.82rem;color:#6B7280;margin:0">Enter a name and email above, or pick a sample lead from the sidebar.</p>
    </div>""", unsafe_allow_html=True)
