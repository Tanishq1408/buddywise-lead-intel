"""Buddywise Lead Intelligence — Simplified UI"""

import streamlit as st, time
from intelligence import analyse_lead, extract_domain, is_personal_email, is_generic_email
from buddywise_context import CASE_STUDY_LEADS, SHOWCASE_LEADS, SAMPLE_LEADS, PRIORITY_MATRIX, PERSON_TIERS

st.set_page_config(page_title="Buddywise Lead Intel", page_icon="🦺", layout="wide")

st.markdown("""<style>
.block-container{padding:1.2rem 2rem 2rem;max-width:1200px}
.priority-banner{border-radius:12px;padding:16px 22px;margin-bottom:1rem;border-left:5px solid}
.fit-pill{display:inline-block;padding:6px 18px;border-radius:30px;font-size:1rem;font-weight:700;margin-right:8px}
.fact-card{background:#111827;border:1px solid #1F2937;border-radius:10px;padding:14px 18px;text-align:center}
.fact-label{font-size:.68rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin:0 0 4px}
.fact-value{font-size:.95rem;font-weight:600;color:#F9FAFB;margin:0}
.person-card{background:#111827;border:1px solid #1F2937;border-radius:10px;padding:16px 20px}
.tier-badge{display:inline-block;padding:5px 16px;border-radius:20px;font-size:.85rem;font-weight:700;margin-bottom:8px}
.sig-row{background:#111827;border:1px solid #1F2937;border-radius:8px;padding:10px 14px;margin:4px 0;display:flex;gap:10px;align-items:flex-start}
.action-box{background:#111827;border:1px solid #1F2937;border-radius:10px;padding:16px 20px}
.no-fit-card{background:#111827;border:2px solid #374151;border-radius:12px;padding:32px;text-align:center;margin:1rem 0}
.detail{font-size:.82rem;color:#D1D5DB;margin:4px 0}
.caution{background:#1C1007;border:1px solid #78350F;border-radius:6px;padding:6px 10px;font-size:.79rem;color:#FCD34D;margin:4px 0}
div[data-testid="stButton"]>button{background:#2563EB;color:#fff;border:none;border-radius:8px;font-weight:600}
div[data-testid="stButton"]>button:hover{background:#1D4ED8;color:#fff}
div[data-testid="metric-container"]{background:#111827;border:1px solid #1F2937;border-radius:8px;padding:10px 14px}
</style>""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def pc(p): return PRIORITY_MATRIX.get(p, PRIORITY_MATRIX["QUALIFY"])
def tier_color(t):  return PERSON_TIERS.get(t,{}).get("color","#6B7280")
def tier_label(t):  return PERSON_TIERS.get(t,{}).get("label", t.replace("_"," ").title())
def tier_desc(t):   return PERSON_TIERS.get(t,{}).get("description","")
def sig_emoji(s):   return {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡"}.get(s,"⚪")
def sl_label(l):    return {"HOT":"🔥 HOT","WARM":"🌡️ WARM","LUKEWARM":"❄️ LUKEWARM","COLD":"🧊 COLD"}.get(l,l)
def sl_color(l):    return {"HOT":"#EF4444","WARM":"#F97316","LUKEWARM":"#EAB308","COLD":"#6B7280"}.get(l,"#6B7280")
def fit_yn(label):
    if label in ("STRONG FIT","GOOD FIT"): return "YES", "#059669", "✅"
    if label == "POSSIBLE FIT":            return "MAYBE", "#D97706", "⚠️"
    return "NO", "#EF4444", "❌"

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
    with st.expander("Copy-paste table", expanded=False):
        import pandas as pd
        st.dataframe(pd.DataFrame([{"Name":l["name"],"Email":l["email"],"Company":l["company"]} for l in SAMPLE_LEADS]),
                     use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Tanishq Singh · HTW Berlin\nBuddywise Case Study · July 2025")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""<div style="display:flex;align-items:center;gap:10px;padding-bottom:1rem;border-bottom:1px solid #1F2937;margin-bottom:1rem">
  <span style="font-size:1.8rem">🦺</span>
  <div><p style="font-size:1.3rem;font-weight:700;color:#F9FAFB;margin:0">Buddywise Lead Intelligence</p>
  <p style="font-size:.78rem;color:#6B7280;margin:0">Paste an email. Get a decision.</p></div>
</div>""", unsafe_allow_html=True)

# ── FORM ─────────────────────────────────────────────────────────────────────
_lead = {}
_sel = st.session_state.get("lead_selector","— type manually —")
if _sel and _sel != "— type manually —":
    for _l in SAMPLE_LEADS:
        if f"{_l['name']} · {_l['company']}" == _sel:
            _lead = _l; break

c1,c2,c3,c4 = st.columns([2.5,2.5,2,1])
with c1: name    = st.text_input("Full Name",         value=_lead.get("name",""),    placeholder="e.g. Markus Kamieth")
with c2: email   = st.text_input("Email Address",     value=_lead.get("email",""),   placeholder="e.g. m.kamieth@basf.com")
with c3: company = st.text_input("Company (optional)",value=_lead.get("company",""), placeholder="Auto-detected")
with c4:
    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
    go = st.button("🔍 Analyse", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if email and "@" in email:
    if is_personal_email(email):
        st.warning("📧 Personal email — company association unclear. Analysing with lower confidence.")
    elif is_generic_email(email):
        st.warning("📬 Generic routing email — this may not be a personal contact.")

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if go:
    if not name.strip(): st.error("Please enter a name."); st.stop()
    if not email.strip() or "@" not in email: st.error("Please enter a valid email."); st.stop()
    api_key = get_gemini_key() if use_gemini else get_api_key()
    if not api_key:
        st.error(f"No API key. Add your {'Google' if use_gemini else 'Anthropic'} key in the sidebar."); st.stop()

    with st.spinner("Analysing..."):
        try:
            t0 = time.time()
            r = analyse_lead(api_key, name.strip(), email.strip(), company.strip() or None,
                             provider="gemini" if use_gemini else "claude")
            elapsed = round(time.time()-t0,1)
        except Exception as e:
            err = str(e)
            if "credit balance" in err or "insufficient" in err.lower():
                st.error("💳 Claude credits exhausted. Add credits at console.anthropic.com → Billing, or switch to Gemini (Free) in the sidebar.")
            elif "quota" in err.lower() or "rate" in err.lower():
                st.error("⏱️ Rate limit hit. Wait 30 seconds and try again.")
            elif "invalid" in err.lower() and "key" in err.lower():
                st.error("🔑 Invalid API key. Check the sidebar.")
            else:
                st.error(f"Analysis failed: {err}")
            st.stop()

    co   = r.get("company",{})
    pe   = r.get("person",{})
    sigs = r.get("buying_signals",[])
    sig_total = r.get("buying_signal_total",0)
    sig_lbl   = r.get("buying_signal_label","COLD")
    act  = r.get("sales_action",{})
    conf = r.get("confidence",{})
    priority  = act.get("priority","QUALIFY")
    cfg = pc(priority)
    hx  = cfg["hex_color"]
    bg  = cfg["bg_hex"]
    co_score  = co.get("fit_score",0)
    pe_score  = pe.get("person_score",0)
    fit_label = co.get("fit_label","UNKNOWN")
    pe_tier   = pe.get("person_tier","CONNECTOR")
    yn, yn_color, yn_emoji = fit_yn(fit_label)

    # ── PRIORITY BANNER ────────────────────────────────────────────────────────
    st.markdown(f"""<div class="priority-banner" style="background:{bg};border-left-color:{hx};border:1px solid {hx}33">
      <p style="font-size:1.4rem;font-weight:800;color:{hx};margin:0">{cfg['emoji']} {cfg['label']}</p>
      <p style="font-size:.85rem;color:#D1D5DB;margin:3px 0 0">{cfg['action']} &nbsp;·&nbsp; <span style="color:{hx};font-weight:600">{cfg['sla']}</span></p>
    </div>""", unsafe_allow_html=True)

    # ── COMPANY FIT: YES / MAYBE / NO ─────────────────────────────────────────
    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem">
      <span class="fit-pill" style="background:{yn_color}22;color:{yn_color};border:1.5px solid {yn_color}55">
        {yn_emoji} Company Fit: {yn}
      </span>
      <span style="font-size:.83rem;color:#9CA3AF">{co.get('name','—')} · {co.get('industry','—')}</span>
    </div>""", unsafe_allow_html=True)

    # ── NO FIT — MINIMAL VIEW ──────────────────────────────────────────────────
    if yn == "NO":
        st.markdown(f"""<div class="no-fit-card">
          <p style="font-size:1.5rem;margin:0">📭</p>
          <p style="font-size:1.1rem;font-weight:700;color:#F9FAFB;margin:8px 0 4px">Not a Buddywise prospect</p>
          <p style="font-size:.85rem;color:#6B7280;margin:0 auto;max-width:480px">{co.get('fit_reasoning',"This company does not match Buddywise ideal customer profile.")}</p>
          <p style="font-size:.78rem;color:#4B5563;margin:16px 0 0">Move on. Don't invest more time here.</p>
        </div>""", unsafe_allow_html=True)
        with st.expander("Why not a fit — details", expanded=False):
            st.markdown(f"**Industry:** {co.get('industry','—')} ({co.get('industry_tier','—')})")
            st.markdown(f"**Size:** {co.get('size_employees','—')} employees")
            st.markdown(f"**Headquarters:** {co.get('headquarters','—')}")
            st.caption(f"Company fit score: {co_score}/100  ·  Analysed in {elapsed}s")
        st.stop()

    # ── YES / MAYBE — FULL VIEW ────────────────────────────────────────────────

    # Quick fact strip
    f1,f2,f3,f4 = st.columns(4)
    with f1:
        st.markdown(f"""<div class="fact-card">
          <p class="fact-label">Industry</p>
          <p class="fact-value">{co.get('industry','—')}</p>
        </div>""", unsafe_allow_html=True)
    with f2:
        st.markdown(f"""<div class="fact-card">
          <p class="fact-label">Employees</p>
          <p class="fact-value">{co.get('size_employees','—')}</p>
        </div>""", unsafe_allow_html=True)
    with f3:
        st.markdown(f"""<div class="fact-card">
          <p class="fact-label">Revenue</p>
          <p class="fact-value">{co.get('revenue_estimate','—')}</p>
        </div>""", unsafe_allow_html=True)
    with f4:
        st.markdown(f"""<div class="fact-card">
          <p class="fact-label">Headquarters</p>
          <p class="fact-value">{co.get('headquarters','—')}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:.8rem 0'></div>", unsafe_allow_html=True)

    # ── PERSON + SIGNALS in one row ────────────────────────────────────────────
    p_col, s_col = st.columns([1,1])

    with p_col:
        tc = tier_color(pe_tier)
        tl = tier_label(pe_tier)
        td = tier_desc(pe_tier)
        st.markdown(f"""<div class="person-card">
          <p style="font-size:.68rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin:0 0 10px">👤 Person</p>
          <p style="font-size:1.1rem;font-weight:700;color:#F9FAFB;margin:0 0 2px">{pe.get('name',name)}</p>
          <p style="font-size:.82rem;color:#9CA3AF;margin:0 0 10px">{pe.get('likely_role','—')}</p>
          <span class="tier-badge" style="background:{tc}22;color:{tc};border:1.5px solid {tc}44">{tl}</span>
          <p style="font-size:.78rem;color:#6B7280;margin:6px 0 0">{td}</p>
          {f'<p style="font-size:.82rem;color:#D1D5DB;margin:10px 0 0;border-top:1px solid #1F2937;padding-top:8px">💡 {pe["key_insight"]}</p>' if pe.get("key_insight") else ""}
        </div>""", unsafe_allow_html=True)

    with s_col:
        slc = sl_color(sig_lbl)
        st.markdown(f"""<div class="person-card">
          <p style="font-size:.68rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin:0 0 10px">📡 Buying Signals</p>
          <span class="tier-badge" style="background:{slc}22;color:{slc};border:1.5px solid {slc}44">{sl_label(sig_lbl)}</span>
        </div>""", unsafe_allow_html=True)
        if sigs:
            for sig in sigs[:3]:
                sc = {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308"}.get(sig.get("strength",""),"#6B7280")
                st.markdown(f"""<div class="sig-row" style="border-left:3px solid {sc}">
                  <span>{sig_emoji(sig.get('strength',''))}</span>
                  <div>
                    <p style="font-size:.83rem;font-weight:600;color:#F9FAFB;margin:0">{sig.get('signal_name','—')}</p>
                    <p style="font-size:.76rem;color:#9CA3AF;margin:2px 0 0">{sig.get('evidence','—')}</p>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:.82rem;color:#4B5563;margin:.5rem 0'>No active buying signals detected. Standard sales cycle expected.</p>", unsafe_allow_html=True)

    st.markdown("<div style='margin:.8rem 0'></div>", unsafe_allow_html=True)

    # ── SALES ACTION — MINIMAL ─────────────────────────────────────────────────
    subj   = act.get("subject_line","—")
    angle  = act.get("opening_angle","—")
    ns_key = act.get("next_step","DISCOVERY_CALL")
    ns_txt = act.get("next_step_text","")
    caut   = act.get("critical_caution","")

    ns_color = {"DEMO_REQUEST":"#059669","DISCOVERY_CALL":"#3B82F6","CONTENT_SEND":"#D97706","LINKEDIN_CONNECT":"#8B5CF6","FIND_CHAMPION":"#F97316"}.get(ns_key,"#6B7280")

    a1, a2 = st.columns([1,1])
    with a1:
        st.markdown("""<div class="action-box"><p style="font-size:.68rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin:0 0 10px">📧 What to send</p></div>""", unsafe_allow_html=True)
        st.markdown("**Subject line**")
        st.code(subj, language=None)
        st.markdown(f"<p class='detail'>{angle}</p>", unsafe_allow_html=True)

    with a2:
        st.markdown("""<div class="action-box"><p style="font-size:.68rem;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin:0 0 10px">▶ Next step</p></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:{ns_color}22;border:1px solid {ns_color}44;border-radius:8px;padding:12px 16px;margin-bottom:8px">
          <p style="color:{ns_color};font-weight:700;font-size:.9rem;margin:0">{ns_key.replace('_',' ')}</p>
          <p style="color:#D1D5DB;font-size:.82rem;margin:4px 0 0">{ns_txt}</p>
        </div>""", unsafe_allow_html=True)
        if caut:
            st.markdown(f'<div class="caution">⚡ {caut}</div>', unsafe_allow_html=True)

    # ── SCORES — COLLAPSED AT BOTTOM ──────────────────────────────────────────
    st.markdown("<div style='margin:.8rem 0'></div>", unsafe_allow_html=True)
    with st.expander(f"📊 Scores & full breakdown  ·  Analysed in {elapsed}s", expanded=False):
        e1, e2, e3 = st.columns(3)
        e1.metric("Company Fit", f"{co_score}/100", fit_label)
        e2.metric("Person Score", f"{pe_score}/100", tier_label(pe_tier))
        e3.metric("Buying Signal", f"{sig_total}/100", sl_label(sig_lbl))

        st.markdown("---")
        st.markdown("**Company score breakdown**")
        bd = co.get("score_breakdown",{})
        for k,lbl,mx in [("industry_fit","Industry (max 40)",40),("company_size","Size (max 25)",25),("geography","Geography (max 20)",20),("physical_site_risk","Physical Risk (max 15)",15)]:
            v = bd.get(k,0)
            c1_,c2_ = st.columns([4,1])
            c1_.caption(lbl); c1_.progress(v/mx if mx else 0)
            c2_.markdown(f"<p style='color:#F9FAFB;font-weight:700;margin-top:18px'>{v}</p>", unsafe_allow_html=True)

        st.markdown("**Person score breakdown**")
        pb = pe.get("score_breakdown",{})
        for k,lbl,mx in [("decision_authority","Decision Authority (max 50)",50),("seniority","Seniority (max 30)",30),("engagement_signal","Engagement Signal (max 20)",20)]:
            v = pb.get(k,0)
            c1_,c2_ = st.columns([4,1])
            c1_.caption(lbl); c1_.progress(v/mx if mx else 0)
            c2_.markdown(f"<p style='color:#F9FAFB;font-weight:700;margin-top:18px'>{v}</p>", unsafe_allow_html=True)

        st.markdown("**Company detail**")
        ops = co.get("physical_operations","")
        hazards = co.get("known_hazards",[])
        features = co.get("buddywise_relevant_features",[])
        if ops: st.markdown(f"**Operations:** {ops}")
        if hazards: st.markdown(f"**Hazards:** {', '.join(hazards[:4])}")
        if features: st.markdown(f"**Buddywise features:** {', '.join(features[:4])}")
        st.markdown(f"**Why this score:** {co.get('fit_reasoning','—')}")
        st.markdown(f"**Person insight:** {pe.get('tier_reasoning','—')}")
        if conf.get("data_notes"): st.caption(conf["data_notes"])

        with st.expander("Raw JSON", expanded=False): st.json(r)

else:
    st.markdown("""<div style="background:#111827;border:1px dashed #374151;border-radius:12px;padding:40px;text-align:center;margin:1.5rem 0">
      <p style="font-size:2rem;margin:0">🦺</p>
      <p style="font-size:1rem;font-weight:600;color:#F9FAFB;margin:8px 0 3px">Paste an inbound email. Get a decision.</p>
      <p style="font-size:.82rem;color:#6B7280;margin:0">Enter a name and email above, or pick a sample lead from the sidebar.</p>
    </div>""", unsafe_allow_html=True)
