"""Buddywise Lead Intelligence"""

import streamlit as st, time
from intelligence import analyse_lead, extract_domain, is_personal_email, is_generic_email
from buddywise_context import CASE_STUDY_LEADS, SHOWCASE_LEADS, SAMPLE_LEADS, PRIORITY_MATRIX, PERSON_TIERS

st.set_page_config(page_title="Buddywise Lead Intel", page_icon="🦺", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif}
.block-container{padding:1.4rem 2.4rem 2rem;max-width:1300px}

/* BANNER */
.priority-banner{border-radius:14px;padding:20px 26px;margin-bottom:1.4rem;display:flex;align-items:center;gap:18px;border:1.5px solid}

/* VERDICT TILES */
.verdict-tile{border-radius:14px;padding:22px 16px;text-align:center;border:1.5px solid;height:115px;display:flex;flex-direction:column;justify-content:center}
.vt-category{font-size:.59rem;text-transform:uppercase;letter-spacing:1.4px;font-weight:700;margin:0 0 8px;opacity:.7}
.vt-main{font-size:1.25rem;font-weight:800;margin:0 0 5px;line-height:1.2}
.vt-sub{font-size:.73rem;margin:0;opacity:.75;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* CARDS */
.intel-card{background:#0D1117;border:1px solid #1F2937;border-radius:14px;padding:20px;margin-bottom:.8rem;height:100%}
.card-hdr{font-size:.61rem;text-transform:uppercase;letter-spacing:1.2px;font-weight:700;color:#4B5563;border-bottom:1px solid #1F2937;padding-bottom:8px;margin-bottom:14px}
.cname{font-size:1.1rem;font-weight:700;color:#F9FAFB;margin:0 0 2px}
.cmeta{font-size:.79rem;color:#6B7280;margin:0 0 12px}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.72rem;font-weight:700;margin:2px 2px 8px 0}
.kv{font-size:.8rem;color:#D1D5DB;margin:5px 0;display:flex;gap:8px}
.kv-icon{flex-shrink:0;width:16px;opacity:.6}
.insight{border-radius:8px;padding:9px 12px;margin:10px 0;font-size:.8rem;border-left:3px solid;line-height:1.45}
.sig-row{border-radius:8px;padding:10px 13px;margin:5px 0;border-left:3px solid;background:#0D1117;border:1px solid #1F2937}
.sig-name{font-size:.81rem;font-weight:600;color:#F9FAFB;margin:0 0 2px}
.sig-ev{font-size:.73rem;color:#6B7280;margin:0;line-height:1.4}

/* ACTION */
.action-card{background:#0D1117;border:1px solid #1F2937;border-radius:14px;padding:20px 22px}
.ns-box{border-radius:10px;padding:13px 16px;margin-bottom:8px;border:1.5px solid}
.caution{background:#1C1007;border:1px solid #78350F;border-radius:6px;padding:7px 11px;font-size:.77rem;color:#FCD34D;margin:6px 0}

.empty-state{background:#0D1117;border:1px dashed #1F2937;border-radius:14px;padding:52px;text-align:center}
div[data-testid="stButton"]>button{background:#2563EB;color:#fff;border:none;border-radius:9px;font-weight:600;font-size:.9rem;height:42px}
div[data-testid="stButton"]>button:hover{background:#1D4ED8;color:#fff}
div[data-testid="stTextInput"] input{background:#0D1117;border:1px solid #1F2937;border-radius:9px;color:#F9FAFB}
</style>""", unsafe_allow_html=True)

# ── COLOR SYSTEM ──────────────────────────────────────────────────────────────
COLORS = {
    "green":  {"bg":"#052E16","border":"#059669","main":"#34D399","sub":"#86EFAC","dark":"#064E3B"},
    "orange": {"bg":"#431407","border":"#D97706","main":"#FCD34D","sub":"#FBBF24","dark":"#451A03"},
    "red":    {"bg":"#450A0A","border":"#EF4444","main":"#FCA5A5","sub":"#F87171","dark":"#4C0519"},
    "gray":   {"bg":"#111827","border":"#374151","main":"#9CA3AF","sub":"#6B7280","dark":"#1F2937"},
}

def C(level): return COLORS.get(level, COLORS["gray"])

def fit_level(lbl):
    return "green" if lbl in ("STRONG FIT","GOOD FIT") else "orange" if lbl=="POSSIBLE FIT" else "red"

def person_level(tier):
    return "green" if tier=="DECISION_MAKER" else "orange" if tier=="INFLUENTIAL" else "gray"

def urgency_level(lbl):
    return "green" if lbl=="HOT" else "orange" if lbl in ("WARM","LUKEWARM") else "gray"

def priority_level(p):
    return "green" if p=="FAST_TRACK" else "orange" if p in ("PURSUE","QUALIFY","NURTURE") else "red"

def verdict_tile(category_icon, category, main_text, sub_text, level):
    c = C(level)
    return f"""<div class="verdict-tile" style="background:{c['bg']};border-color:{c['border']}">
      <p class="vt-category" style="color:{c['sub']}">{category_icon} {category}</p>
      <p class="vt-main" style="color:{c['main']}">{main_text}</p>
      <p class="vt-sub" style="color:{c['sub']}">{sub_text}</p>
    </div>"""

def pc(p): return PRIORITY_MATRIX.get(p, PRIORITY_MATRIX["QUALIFY"])
def tier_label(t): return PERSON_TIERS.get(t,{}).get("label", t.replace("_"," ").title())
def tier_desc(t):  return PERSON_TIERS.get(t,{}).get("description","")
def urg_label(l):  return {"HOT":"🔥 HOT","WARM":"🌡️ WARM","LUKEWARM":"❄️ LUKEWARM","COLD":"🧊 COLD"}.get(l,l)
def sig_emoji(s):  return {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡"}.get(s,"⚪")

def get_api_key():
    try: return st.secrets["ANTHROPIC_API_KEY"]
    except: return st.session_state.get("api_key","")

def get_gemini_key():
    try: return st.secrets["GOOGLE_API_KEY"]
    except: return st.session_state.get("gemini_key","")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦺 Lead Intel")
    st.markdown("---")
    provider = st.radio("AI Provider", ["Claude (Anthropic)","Gemini (Google — Free)"], index=0)
    use_gemini = "Gemini" in provider
    try:
        _ = st.secrets["GOOGLE_API_KEY"] if use_gemini else st.secrets["ANTHROPIC_API_KEY"]
    except:
        lbl = "Google AI Key" if use_gemini else "Anthropic Key"
        ph  = "AIza..." if use_gemini else "sk-ant-..."
        key_in = st.text_input(lbl, type="password", placeholder=ph, label_visibility="collapsed")
        if key_in:
            st.session_state["gemini_key" if use_gemini else "api_key"] = key_in
        if use_gemini:
            st.markdown("[Get free key →](https://aistudio.google.com/apikey)", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Select a Lead**")
    opts = ["— type manually —"] + [f"{l['name']} · {l['company']}" for l in SAMPLE_LEADS]
    chosen = st.selectbox("Lead", opts, key="lead_selector", label_visibility="collapsed")
    with st.expander("Copy-paste table"):
        import pandas as pd
        st.dataframe(pd.DataFrame([{"Name":l["name"],"Email":l["email"],"Company":l["company"]}
                                    for l in SAMPLE_LEADS]), use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Tanishq Singh · HTW Berlin\nBuddywise Case Study · July 2025")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding-bottom:1.1rem;border-bottom:1px solid #1F2937;margin-bottom:1.2rem">
  <span style="font-size:1.9rem;line-height:1">🦺</span>
  <div>
    <p style="font-size:1.25rem;font-weight:800;color:#F9FAFB;margin:0;letter-spacing:-.3px">Buddywise Lead Intelligence</p>
    <p style="font-size:.75rem;color:#4B5563;margin:1px 0 0">Paste an email. Get a decision in seconds.</p>
  </div>
</div>""", unsafe_allow_html=True)

# ── FORM ─────────────────────────────────────────────────────────────────────
_lead = {}
_sel  = st.session_state.get("lead_selector","— type manually —")
if _sel and _sel != "— type manually —":
    for _l in SAMPLE_LEADS:
        if f"{_l['name']} · {_l['company']}" == _sel:
            _lead = _l; break

c1,c2,c3,c4 = st.columns([2.8, 2.8, 2, 1])
with c1: name    = st.text_input("Full Name",          value=_lead.get("name",""),    placeholder="Markus Kamieth")
with c2: email   = st.text_input("Email Address",      value=_lead.get("email",""),   placeholder="m.kamieth@basf.com")
with c3: company = st.text_input("Company (optional)", value=_lead.get("company",""), placeholder="Auto-detected")
with c4:
    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
    go = st.button("🔍 Analyse", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if email and "@" in email and is_personal_email(email):
    st.warning("📧 Personal email — company unclear. Analysing with lower confidence.")
elif email and "@" in email and is_generic_email(email):
    st.warning("📬 Generic routing email — may not be a personal contact.")

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if go:
    if not name.strip():                           st.error("Please enter a name."); st.stop()
    if not email.strip() or "@" not in email:      st.error("Please enter a valid email."); st.stop()
    api_key = get_gemini_key() if use_gemini else get_api_key()
    if not api_key:
        st.error(f"No API key. Add your {'Google' if use_gemini else 'Anthropic'} key in the sidebar."); st.stop()

    with st.spinner(""):
        try:
            t0 = time.time()
            r  = analyse_lead(api_key, name.strip(), email.strip(), company.strip() or None,
                              provider="gemini" if use_gemini else "claude")
            elapsed = round(time.time()-t0, 1)
        except Exception as e:
            err = str(e)
            if "credit balance" in err or "insufficient" in err.lower():
                st.error("💳 Claude credits exhausted. Add credits at console.anthropic.com or switch to Gemini (Free)."); st.stop()
            elif "quota" in err.lower() or "rate" in err.lower():
                st.error("⏱️ Rate limit hit. Wait 30 seconds and retry."); st.stop()
            else:
                st.error(f"Analysis failed: {err}"); st.stop()

    co       = r.get("company",{})
    pe       = r.get("person",{})
    sigs     = r.get("buying_signals",[])
    sig_tot  = r.get("buying_signal_total", 0)
    sig_lbl  = r.get("buying_signal_label", "COLD")
    act      = r.get("sales_action",{})
    conf     = r.get("confidence",{})
    priority = act.get("priority","QUALIFY")
    cfg      = pc(priority)
    hx       = cfg["hex_color"];  bg = cfg["bg_hex"]

    fit_lbl  = co.get("fit_label","UNKNOWN")
    pe_tier  = pe.get("person_tier","CONNECTOR")
    co_score = co.get("fit_score",0)
    pe_score = pe.get("person_score",0)
    is_match = fit_lbl not in ("NOT A FIT","WEAK FIT")

    fl = fit_level(fit_lbl)
    pl = person_level(pe_tier)
    ul = urgency_level(sig_lbl)
    pvl= priority_level(priority)
    Cp = C(pvl)

    # ── PRIORITY BANNER ────────────────────────────────────────────────────────
    st.markdown(f"""<div class="priority-banner" style="background:{Cp['bg']};border-color:{Cp['border']}">
      <span style="font-size:2.6rem;line-height:1;flex-shrink:0">{cfg['emoji']}</span>
      <div style="flex:1">
        <p style="font-size:1.55rem;font-weight:800;color:{Cp['main']};margin:0;letter-spacing:-.3px">{cfg['label']}</p>
        <p style="font-size:.84rem;color:#D1D5DB;margin:3px 0 0">{cfg['action']}</p>
      </div>
      <div style="text-align:right;flex-shrink:0">
        <p style="font-size:.9rem;font-weight:600;color:{Cp['main']};margin:0">{cfg['sla']}</p>
        <p style="font-size:.72rem;color:{Cp['sub']};margin:2px 0 0">{co.get('name','—')} · {elapsed}s</p>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── 3 VERDICT TILES ────────────────────────────────────────────────────────
    t1,t2,t3 = st.columns(3)
    with t1: st.markdown(verdict_tile("🏭","Industry Match", fit_lbl, co.get('industry','—'), fl), unsafe_allow_html=True)
    with t2: st.markdown(verdict_tile("👤","Person Relevance", tier_label(pe_tier), pe.get('likely_role','—'), pl), unsafe_allow_html=True)
    with t3: st.markdown(verdict_tile("⚡","Purchase Timing", urg_label(sig_lbl), f"{len(sigs)} trigger{'s' if len(sigs)!=1 else ''} detected", ul), unsafe_allow_html=True)

    st.markdown("<div style='margin:.7rem 0'></div>", unsafe_allow_html=True)

    # ── 3 DETAIL CARDS ─────────────────────────────────────────────────────────
    col_co, col_pe, col_urg = st.columns(3)
    Cf = C(fl); Cp2 = C(pl); Cu = C(ul)

    # COMPANY
    with col_co:
        st.markdown(f"""<div class="intel-card" style="border-color:{Cf['border']}44">
          <div class="card-hdr">Company</div>
          <p class="cname">{co.get('name','Unknown')}</p>
          <p class="cmeta">{co.get('headquarters','—')}</p>
          <span class="badge" style="background:{Cf['bg']};color:{Cf['main']};border:1px solid {Cf['border']}55">{fit_lbl}</span>
        </div>""", unsafe_allow_html=True)

        for ico,txt in [("👥",f"{co.get('size_employees','—')} employees"),
                        ("💰",f"{co.get('revenue_estimate','—')} revenue"),
                        ("🌍",f"{', '.join(co.get('countries_operating',[])[:2])} operations")]:
            st.markdown(f"<div class='kv'><span class='kv-icon'>{ico}</span><span>{txt}</span></div>", unsafe_allow_html=True)

        if is_match:
            hazards = co.get("known_hazards",[])
            if hazards:
                st.markdown(f"<div class='insight' style='background:{Cf['bg']};border-left-color:{Cf['border']};color:{Cf['sub']}'>⚠ {' · '.join(hazards[:3])}</div>", unsafe_allow_html=True)
            feats = co.get("buddywise_relevant_features",[])
            if feats:
                st.markdown(f"<div class='insight' style='background:#0D1117;border-left-color:#3B82F6;color:#93C5FD'>✓ {' · '.join(feats[:3])}</div>", unsafe_allow_html=True)
            if co.get("fit_reasoning"):
                st.markdown(f"<div class='insight' style='background:{Cf['bg']};border-left-color:{Cf['border']};color:{Cf['sub']}'>💡 {co['fit_reasoning']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='insight' style='background:{Cf['bg']};border-left-color:{Cf['border']};color:{Cf['sub']}'>❌ {co.get('fit_reasoning','Does not match Buddywise ICP.')}</div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:.78rem;color:#4B5563;margin-top:6px;text-align:center'>Move on. This is not a Buddywise prospect.</p>", unsafe_allow_html=True)

    # PERSON
    with col_pe:
        st.markdown(f"""<div class="intel-card" style="border-color:{Cp2['border']}44">
          <div class="card-hdr">Person</div>
          <p class="cname">{pe.get('name',name)}</p>
          <p class="cmeta">{pe.get('likely_role','—')}</p>
          <span class="badge" style="background:{Cp2['bg']};color:{Cp2['main']};border:1px solid {Cp2['border']}55">{tier_label(pe_tier)}</span>
        </div>""", unsafe_allow_html=True)

        for ico,txt in [("🏢",f"{pe.get('department','—')} department"),
                        ("💰",f"Budget relevance: {pe.get('budget_relevance','—')}")]:
            st.markdown(f"<div class='kv'><span class='kv-icon'>{ico}</span><span>{txt}</span></div>", unsafe_allow_html=True)

        td = tier_desc(pe_tier)
        if td:
            st.markdown(f"<div class='insight' style='background:{Cp2['bg']};border-left-color:{Cp2['border']};color:{Cp2['sub']}'>{td}</div>", unsafe_allow_html=True)
        if pe.get("key_insight"):
            st.markdown(f"<div class='insight' style='background:#0D1117;border-left-color:#8B5CF6;color:#C4B5FD'>💡 {pe['key_insight']}</div>", unsafe_allow_html=True)
        if pe.get("tier_reasoning"):
            st.markdown(f"<div class='kv' style='color:#4B5563;font-size:.76rem;margin-top:6px'><span>→</span><span>{pe['tier_reasoning']}</span></div>", unsafe_allow_html=True)

    # PURCHASE TIMING
    with col_urg:
        st.markdown(f"""<div class="intel-card" style="border-color:{Cu['border']}44">
          <div class="card-hdr">Purchase Timing</div>
          <p class="cname" style="color:{Cu['main']}">{urg_label(sig_lbl)}</p>
          <p class="cmeta">{len(sigs)} signal{'s' if len(sigs)!=1 else ''} detected</p>
        </div>""", unsafe_allow_html=True)

        if sigs:
            for sig in sigs[:3]:
                sc = {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308"}.get(sig.get("strength",""),"#6B7280")
                sbg= {"CRITICAL":"#450A0A","HIGH":"#431407","MEDIUM":"#2D1B00"}.get(sig.get("strength",""),"#111827")
                st.markdown(f"""<div class="sig-row" style="background:{sbg};border-color:{sc}22;border-left-color:{sc}">
                  <p class="sig-name">{sig_emoji(sig.get('strength',''))} {sig.get('signal_name','—')}
                    <span style="float:right;font-size:.7rem;color:{sc}">+{sig.get('score',0)}</span></p>
                  <p class="sig-ev">{sig.get('evidence','—')}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="sig-row" style="background:{Cu['bg']};border-color:{Cu['border']}33;border-left-color:{Cu['border']}">
              <p class="sig-name" style="color:{Cu['main']}">No active triggers</p>
              <p class="sig-ev" style="color:{Cu['sub']}">No immediate urgency signals. Standard sales cycle expected.</p>
            </div>""", unsafe_allow_html=True)

        if not is_match:
            st.markdown("<p style='font-size:.76rem;color:#4B5563;margin-top:8px'>Signals less relevant — company is not a fit.</p>", unsafe_allow_html=True)

    # ── SALES ACTION (only if match) ───────────────────────────────────────────
    if is_match:
        st.markdown("<div style='margin:.7rem 0'></div>", unsafe_allow_html=True)
        subj = act.get("subject_line","—")
        angle= act.get("opening_angle","—")
        ns_k = act.get("next_step","DISCOVERY_CALL")
        ns_t = act.get("next_step_text","")
        caut = act.get("critical_caution","")
        p_why= act.get("priority_reasoning","")

        ns_level = {"DEMO_REQUEST":"green","DISCOVERY_CALL":"green","CONTENT_SEND":"orange","LINKEDIN_CONNECT":"orange","FIND_CHAMPION":"orange"}.get(ns_k,"gray")
        Cns = C(ns_level)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown("""<div class="action-card"><div class="card-hdr">📧 What to send</div></div>""", unsafe_allow_html=True)
            st.markdown("**Subject line**")
            st.code(subj, language=None)
            st.markdown(f"<p style='font-size:.82rem;color:#D1D5DB;margin:4px 0 0'>{angle}</p>", unsafe_allow_html=True)

        with a2:
            st.markdown("""<div class="action-card"><div class="card-hdr">▶ Next step</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="ns-box" style="background:{Cns['bg']};border-color:{Cns['border']}">
              <p style="color:{Cns['main']};font-weight:700;font-size:.95rem;margin:0">{ns_k.replace('_',' ')}</p>
              <p style="color:{Cns['sub']};font-size:.81rem;margin:5px 0 0">{ns_t}</p>
            </div>""", unsafe_allow_html=True)
            if caut:
                st.markdown(f'<div class="caution">⚡ {caut}</div>', unsafe_allow_html=True)
            if p_why:
                st.markdown(f"<p style='font-size:.77rem;color:#4B5563;margin-top:6px'>💡 {p_why}</p>", unsafe_allow_html=True)

    # ── SCORES — BOTTOM EXPANDER ───────────────────────────────────────────────
    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)
    with st.expander("📊 Full scores & breakdown", expanded=False):
        e1,e2,e3 = st.columns(3)
        e1.metric("Company Fit",      f"{co_score}/100",  fit_lbl)
        e2.metric("Person Score",     f"{pe_score}/100",  tier_label(pe_tier))
        e3.metric("Purchase Timing",  f"{sig_tot}/100",   urg_label(sig_lbl))
        st.markdown("---")
        L,R = st.columns(2)
        with L:
            st.markdown("**Company breakdown**")
            for k,lbl,mx in [("industry_fit","Industry (max 40)",40),("company_size","Size (max 25)",25),
                              ("geography","Geography (max 20)",20),("physical_site_risk","Risk (max 15)",15)]:
                v = co.get("score_breakdown",{}).get(k,0)
                ca,cb = st.columns([4,1])
                ca.caption(lbl); ca.progress(v/mx if mx else 0)
                cb.markdown(f"<p style='font-weight:700;color:#F9FAFB;margin-top:18px'>{v}</p>", unsafe_allow_html=True)
        with R:
            st.markdown("**Person breakdown**")
            for k,lbl,mx in [("decision_authority","Authority (max 50)",50),
                              ("seniority","Seniority (max 30)",30),("engagement_signal","Signal (max 20)",20)]:
                v = pe.get("score_breakdown",{}).get(k,0)
                ca,cb = st.columns([4,1])
                ca.caption(lbl); ca.progress(v/mx if mx else 0)
                cb.markdown(f"<p style='font-weight:700;color:#F9FAFB;margin-top:18px'>{v}</p>", unsafe_allow_html=True)
        if conf.get("data_notes"):
            st.caption(conf["data_notes"])
        with st.expander("Raw JSON"): st.json(r)

else:
    st.markdown("""<div class="empty-state">
      <p style="font-size:2.2rem;margin:0">🦺</p>
      <p style="font-size:1rem;font-weight:700;color:#F9FAFB;margin:10px 0 4px">Paste an inbound email. Get a decision.</p>
      <p style="font-size:.8rem;color:#4B5563;margin:0">Enter a name and email above, or select a sample lead from the sidebar.</p>
    </div>""", unsafe_allow_html=True)
