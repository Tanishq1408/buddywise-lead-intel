"""Buddywise Lead Intelligence"""
import streamlit as st, time
from intelligence import analyse_lead, is_personal_email, is_generic_email
from buddywise_context import SAMPLE_LEADS, PRIORITY_MATRIX, PERSON_TIERS

st.set_page_config(page_title="Buddywise Lead Intel", page_icon="🦺", layout="wide")
st.markdown("""<style>
.block-container{padding:1.2rem 2.2rem 2rem;max-width:1280px}
/* BANNER */
.banner{border-radius:12px;padding:16px 24px;margin-bottom:1.2rem;display:flex;align-items:center;gap:16px;border:1.5px solid}
/* TILES - auto height, no clipping */
.tile{border-radius:12px;padding:20px 16px;text-align:center;border:1.5px solid;margin-bottom:.9rem}
.tile-cat{font-size:.6rem;text-transform:uppercase;letter-spacing:1.3px;font-weight:700;margin:0 0 8px;display:block}
.tile-main{font-size:1.2rem;font-weight:800;margin:0 0 5px;line-height:1.2;display:block}
.tile-sub{font-size:.73rem;margin:0;display:block;line-height:1.4;word-break:break-word}
/* CARDS */
.card{background:#0D1117;border:1px solid #1F2937;border-radius:12px;padding:18px;margin-bottom:.7rem}
.card-hdr{font-size:.59rem;text-transform:uppercase;letter-spacing:1.2px;font-weight:700;color:#4B5563;border-bottom:1px solid #1F2937;padding-bottom:7px;margin-bottom:12px}
.cname{font-size:1.1rem;font-weight:700;color:#F9FAFB;margin:0 0 2px}
.cmeta{font-size:.78rem;color:#6B7280;margin:0 0 10px}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.71rem;font-weight:700;margin:2px 2px 8px 0}
.kv{font-size:.79rem;color:#D1D5DB;margin:4px 0;display:flex;gap:7px}
.ibox{border-radius:8px;padding:8px 12px;margin:8px 0;font-size:.79rem;border-left:3px solid;line-height:1.45}
.sig{border-radius:8px;padding:9px 12px;margin:5px 0;border-left:3px solid}
.sig-n{font-size:.8rem;font-weight:600;color:#F9FAFB;margin:0 0 2px}
.sig-e{font-size:.72rem;color:#6B7280;margin:0;line-height:1.4}
/* ACTION */
.act-card{background:#0D1117;border:1px solid #1F2937;border-radius:12px;padding:18px 20px}
.ns{border-radius:10px;padding:12px 15px;margin-bottom:7px;border:1.5px solid}
.warn{background:#1C1007;border:1px solid #78350F;border-radius:6px;padding:6px 10px;font-size:.76rem;color:#FCD34D;margin:5px 0}
.empty{background:#0D1117;border:1px dashed #1F2937;border-radius:12px;padding:48px;text-align:center}
div[data-testid="stButton"]>button{background:#2563EB;color:#fff;border:none;border-radius:8px;font-weight:600}
div[data-testid="stButton"]>button:hover{background:#1D4ED8;color:#fff}
</style>""", unsafe_allow_html=True)

# COLOR SYSTEM
G={"bg":"#052E16","br":"#059669","main":"#34D399","sub":"#86EFAC"}
O={"bg":"#431407","br":"#D97706","main":"#FCD34D","sub":"#FBBF24"}
R={"bg":"#450A0A","br":"#EF4444","main":"#FCA5A5","sub":"#F87171"}
N={"bg":"#111827","br":"#374151","main":"#9CA3AF","sub":"#6B7280"}

def col(level): return {"green":G,"orange":O,"red":R,"gray":N}.get(level,N)
def fit_lv(l):  return "green" if l in("STRONG FIT","GOOD FIT") else "orange" if l=="POSSIBLE FIT" else "red"
def per_lv(t):  return "green" if t=="DECISION_MAKER" else "orange" if t=="INFLUENTIAL" else "gray"
def urg_lv(l):  return "green" if l=="HOT" else "orange" if l in("WARM","LUKEWARM") else "gray"
def pri_lv(p):  return "green" if p=="FAST_TRACK" else "orange" if p in("PURSUE","NURTURE") else "red"
def urg_str(l): return {"HOT":"🔥 HOT","WARM":"🌡️ WARM","LUKEWARM":"❄️ LUKEWARM","COLD":"🧊 COLD"}.get(l,l)
def sig_e(s):   return {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡"}.get(s,"⚪")
def sig_c(s):   return {"CRITICAL":"#EF4444","HIGH":"#F97316","MEDIUM":"#EAB308"}.get(s,"#6B7280")
def sig_b(s):   return {"CRITICAL":"#450A0A","HIGH":"#431407","MEDIUM":"#2D1B00"}.get(s,"#111827")
def tl(t):      return PERSON_TIERS.get(t,{}).get("label",t.replace("_"," ").title())
def td(t):      return PERSON_TIERS.get(t,{}).get("description","")
def pc(p):      return PRIORITY_MATRIX.get(p,PRIORITY_MATRIX["PURSUE"])

def tile(icon, cat, main, sub, level):
    c=col(level)
    return f'<div class="tile" style="background:{c["bg"]};border-color:{c["br"]}"><span class="tile-cat" style="color:{c["sub"]}">{icon} {cat}</span><span class="tile-main" style="color:{c["main"]}">{main}</span><span class="tile-sub" style="color:{c["sub"]}">{sub}</span></div>'

def get_key(use_gemini):
    try: return st.secrets["GOOGLE_API_KEY"] if use_gemini else st.secrets["ANTHROPIC_API_KEY"]
    except: return st.session_state.get("gemini_key" if use_gemini else "api_key","")

# SIDEBAR
with st.sidebar:
    st.markdown("### 🦺 Lead Intel")
    st.markdown("---")
    provider = st.radio("AI Provider",["Claude (Anthropic)","Gemini (Google — Free)"],index=0)
    use_gem  = "Gemini" in provider
    try:
        _ = st.secrets["GOOGLE_API_KEY"] if use_gem else st.secrets["ANTHROPIC_API_KEY"]
    except:
        lbl = "Google AI Key" if use_gem else "Anthropic Key"
        ki  = st.text_input(lbl,type="password",placeholder="AIza..." if use_gem else "sk-ant-...",label_visibility="collapsed")
        if ki: st.session_state["gemini_key" if use_gem else "api_key"] = ki
        if use_gem: st.markdown("[Get free key →](https://aistudio.google.com/apikey)",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Select a Lead**")
    opts  = ["— type manually —"]+[f"{l['name']} · {l['company']}" for l in SAMPLE_LEADS]
    chosen= st.selectbox("Lead",opts,key="lead_sel",label_visibility="collapsed")
    with st.expander("Copy-paste table"):
        import pandas as pd
        st.dataframe(pd.DataFrame([{"Name":l["name"],"Email":l["email"],"Company":l["company"]} for l in SAMPLE_LEADS]),use_container_width=True,hide_index=True)
    st.markdown("---")
    st.caption("Buddywise Case Study · July 2025")

# HEADER
st.markdown('<div style="display:flex;align-items:center;gap:10px;padding-bottom:1rem;border-bottom:1px solid #1F2937;margin-bottom:1.1rem"><span style="font-size:1.7rem">🦺</span><div><p style="font-size:1.2rem;font-weight:800;color:#F9FAFB;margin:0;letter-spacing:-.3px">Buddywise Lead Intelligence</p><p style="font-size:.73rem;color:#4B5563;margin:1px 0 0">Paste an email. Get a decision.</p></div></div>',unsafe_allow_html=True)

# FORM
_lead={}
_sel=st.session_state.get("lead_sel","— type manually —")
if _sel and _sel!="— type manually —":
    for _l in SAMPLE_LEADS:
        if f"{_l['name']} · {_l['company']}"==_sel: _lead=_l; break

c1,c2,c3,c4=st.columns([2.8,2.8,2,1])
with c1: name   =st.text_input("Full Name",         value=_lead.get("name",""),   placeholder="Markus Kamieth")
with c2: email  =st.text_input("Email Address",     value=_lead.get("email",""),  placeholder="m.kamieth@basf.com")
with c3: company=st.text_input("Company (optional)",value=_lead.get("company",""),placeholder="Auto-detected")
with c4:
    st.markdown("<div style='margin-top:28px'>",unsafe_allow_html=True)
    go=st.button("🔍 Analyse",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

if email and "@" in email:
    if is_personal_email(email): st.warning("📧 Personal email — company unclear. Analysing with lower confidence.")
    elif is_generic_email(email): st.warning("📬 Generic email — may not be a personal contact.")

# ANALYSIS
if go:
    if not name.strip():                       st.error("Please enter a name."); st.stop()
    if not email.strip() or "@" not in email:  st.error("Please enter a valid email."); st.stop()
    api_key=get_key(use_gem)
    if not api_key: st.error(f"No API key. Add your {'Google' if use_gem else 'Anthropic'} key in the sidebar."); st.stop()

    with st.spinner("Analysing..."):
        try:
            t0=time.time()
            r=analyse_lead(api_key,name.strip(),email.strip(),company.strip() or None,provider="gemini" if use_gem else "claude")
            elapsed=round(time.time()-t0,1)
        except Exception as e:
            err=str(e)
            if "credit balance" in err or "insufficient" in err.lower(): st.error("💳 Claude credits exhausted. Add credits at console.anthropic.com or switch to Gemini (Free)."); st.stop()
            elif "quota" in err.lower() or "rate" in err.lower(): st.error("⏱️ Rate limit. Wait 30s and retry."); st.stop()
            else: st.error(f"Analysis failed: {err}"); st.stop()

    co=r.get("company",{}); pe=r.get("person",{}); sigs=r.get("buying_signals",[])
    sig_tot=r.get("buying_signal_total",0); sig_lbl=r.get("buying_signal_label","COLD")
    act=r.get("sales_action",{}); conf=r.get("confidence",{})
    priority=act.get("priority","PURSUE")
    # Map any lingering QUALIFY to PURSUE
    if priority=="QUALIFY": priority="PURSUE"
    cfg=pc(priority)
    hx=cfg["hex_color"]; bg=cfg["bg_hex"]
    fit_lbl=co.get("fit_label","UNKNOWN"); pe_tier=pe.get("person_tier","CONNECTOR")
    co_score=co.get("fit_score",0); pe_score=pe.get("person_score",0)
    is_match=fit_lbl not in("NOT A FIT","WEAK FIT")
    fl=fit_lv(fit_lbl); pl=per_lv(pe_tier); ul=urg_lv(sig_lbl); pvl=pri_lv(priority)
    Cp=col(pvl); Cf=col(fl); Cpe=col(pl); Cu=col(ul)

    # BANNER - clean, no SLA
    st.markdown(f'<div class="banner" style="background:{Cp["bg"]};border-color:{Cp["br"]}"><span style="font-size:2.4rem;line-height:1;flex-shrink:0">{cfg["emoji"]}</span><div style="flex:1"><p style="font-size:1.45rem;font-weight:800;color:{Cp["main"]};margin:0;letter-spacing:-.3px">{cfg["label"]}</p><p style="font-size:.82rem;color:#D1D5DB;margin:2px 0 0">{cfg["action"]}</p></div><p style="font-size:.72rem;color:{Cp["sub"]};margin:0;flex-shrink:0">{co.get("name","—")} · {elapsed}s</p></div>',unsafe_allow_html=True)

    # 3 VERDICT TILES
    t1,t2,t3=st.columns(3)
    with t1: st.markdown(tile("🏭","Industry Match",fit_lbl,co.get("industry","—"),fl),unsafe_allow_html=True)
    with t2: st.markdown(tile("👤","Person Relevance",tl(pe_tier),pe.get("likely_role","—"),pl),unsafe_allow_html=True)
    with t3: st.markdown(tile("⚡","Purchase Timing",urg_str(sig_lbl),f"{len(sigs)} trigger{'s' if len(sigs)!=1 else ''} detected",ul),unsafe_allow_html=True)

    st.markdown("<div style='margin:.5rem 0'></div>",unsafe_allow_html=True)

    # 3 DETAIL CARDS
    col_co,col_pe,col_urg=st.columns(3)

    with col_co:
        st.markdown(f'<div class="card" style="border-color:{Cf["br"]}33"><div class="card-hdr">Company</div><p class="cname">{co.get("name","Unknown")}</p><p class="cmeta">{co.get("headquarters","—")}</p><span class="badge" style="background:{Cf["bg"]};color:{Cf["main"]};border:1px solid {Cf["br"]}44">{fit_lbl}</span></div>',unsafe_allow_html=True)
        for ico,txt in [("👥",f"{co.get('size_employees','—')} employees"),("💰",f"{co.get('revenue_estimate','—')} revenue"),("🌍",f"{', '.join(co.get('countries_operating',[])[:2])}")]:
            st.markdown(f"<div class='kv'><span>{ico}</span><span>{txt}</span></div>",unsafe_allow_html=True)
        if is_match:
            h=co.get("known_hazards",[])
            if h: st.markdown(f"<div class='ibox' style='background:{Cf['bg']};border-left-color:{Cf['br']};color:{Cf['sub']}'>⚠ {' · '.join(h[:3])}</div>",unsafe_allow_html=True)
            f2=co.get("buddywise_relevant_features",[])
            if f2: st.markdown(f"<div class='ibox' style='background:#0D1117;border-left-color:#3B82F6;color:#93C5FD'>✓ {' · '.join(f2[:3])}</div>",unsafe_allow_html=True)
            if co.get("fit_reasoning"): st.markdown(f"<div class='ibox' style='background:{Cf['bg']};border-left-color:{Cf['br']};color:{Cf['sub']}'>💡 {co['fit_reasoning']}</div>",unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ibox' style='background:{Cf['bg']};border-left-color:{Cf['br']};color:{Cf['sub']}'>❌ {co.get('fit_reasoning','Does not match Buddywise ICP.')}</div>",unsafe_allow_html=True)
            st.markdown("<p style='font-size:.76rem;color:#4B5563;text-align:center;margin-top:6px'>Move on. Not a Buddywise prospect.</p>",unsafe_allow_html=True)

    with col_pe:
        st.markdown(f'<div class="card" style="border-color:{Cpe["br"]}33"><div class="card-hdr">Person</div><p class="cname">{pe.get("name",name)}</p><p class="cmeta">{pe.get("likely_role","—")}</p><span class="badge" style="background:{Cpe["bg"]};color:{Cpe["main"]};border:1px solid {Cpe["br"]}44">{tl(pe_tier)}</span></div>',unsafe_allow_html=True)
        for ico,txt in [("🏢",pe.get("department","—")),("💰",f"Budget: {pe.get('budget_relevance','—')}")]:
            st.markdown(f"<div class='kv'><span>{ico}</span><span>{txt}</span></div>",unsafe_allow_html=True)
        t_desc=td(pe_tier)
        if t_desc: st.markdown(f"<div class='ibox' style='background:{Cpe['bg']};border-left-color:{Cpe['br']};color:{Cpe['sub']}'>{t_desc}</div>",unsafe_allow_html=True)
        if pe.get("key_insight"): st.markdown(f"<div class='ibox' style='background:#0D1117;border-left-color:#8B5CF6;color:#C4B5FD'>💡 {pe['key_insight']}</div>",unsafe_allow_html=True)
        if pe.get("tier_reasoning"): st.markdown(f"<p style='font-size:.75rem;color:#4B5563;margin-top:5px'>→ {pe['tier_reasoning']}</p>",unsafe_allow_html=True)

    with col_urg:
        st.markdown(f'<div class="card" style="border-color:{Cu["br"]}33"><div class="card-hdr">Purchase Timing</div><p class="cname" style="color:{Cu["main"]}">{urg_str(sig_lbl)}</p><p class="cmeta">{len(sigs)} trigger{"s" if len(sigs)!=1 else ""} detected</p></div>',unsafe_allow_html=True)
        if sigs:
            for s in sigs[:3]:
                sc=sig_c(s.get("strength","")); sb=sig_b(s.get("strength",""))
                st.markdown(f"<div class='sig' style='background:{sb};border-left-color:{sc}'><p class='sig-n'>{sig_e(s.get('strength',''))} {s.get('signal_name','—')} <span style='float:right;font-size:.69rem;color:{sc}'>+{s.get('score',0)}</span></p><p class='sig-e'>{s.get('evidence','—')}</p></div>",unsafe_allow_html=True)
        else:
            no_bg=Cu["bg"]; no_br=Cu["br"]; no_main=Cu["main"]; no_sub=Cu["sub"]
            st.markdown(f"<div class='sig' style='background:{no_bg};border-left-color:{no_br}'><p class='sig-n' style='color:{no_main}'>No active triggers</p><p class='sig-e' style='color:{no_sub}'>Standard sales cycle. No immediate urgency.</p></div>",unsafe_allow_html=True)
        if not is_match:
            st.markdown("<p style='font-size:.74rem;color:#4B5563;margin-top:6px'>Signals less relevant — company not a fit.</p>",unsafe_allow_html=True)

    # SALES ACTION (only if match)
    if is_match:
        st.markdown("<div style='margin:.6rem 0'></div>",unsafe_allow_html=True)
        subj=act.get("subject_line","—"); angle=act.get("opening_angle","—")
        ns_k=act.get("next_step","DISCOVERY_CALL"); ns_t=act.get("next_step_text","")
        caut=act.get("critical_caution",""); p_why=act.get("priority_reasoning","")
        ns_c=col({"DEMO_REQUEST":"green","DISCOVERY_CALL":"green","CONTENT_SEND":"orange","LINKEDIN_CONNECT":"orange","FIND_CHAMPION":"orange"}.get(ns_k,"gray"))
        a1,a2=st.columns(2)
        with a1:
            st.markdown('<div class="act-card"><div class="card-hdr">📧 What to send</div></div>',unsafe_allow_html=True)
            st.markdown("**Subject line**"); st.code(subj,language=None)
            st.markdown(f"<p style='font-size:.8rem;color:#D1D5DB;margin:3px 0 0'>{angle}</p>",unsafe_allow_html=True)
        with a2:
            st.markdown('<div class="act-card"><div class="card-hdr">▶ Next step</div></div>',unsafe_allow_html=True)
            ns_bg=ns_c["bg"]; ns_br=ns_c["br"]; ns_main=ns_c["main"]; ns_sub=ns_c["sub"]; ns_lbl=ns_k.replace("_"," ")
            st.markdown(f"<div class='ns' style='background:{ns_bg};border-color:{ns_br}'><p style='color:{ns_main};font-weight:700;font-size:.92rem;margin:0'>{ns_lbl}</p><p style='color:{ns_sub};font-size:.8rem;margin:4px 0 0'>{ns_t}</p></div>",unsafe_allow_html=True)
            if caut: st.markdown(f'<div class="warn">⚡ {caut}</div>',unsafe_allow_html=True)
            if p_why: st.markdown(f"<p style='font-size:.75rem;color:#4B5563;margin-top:5px'>💡 {p_why}</p>",unsafe_allow_html=True)

    # SCORES - BOTTOM
    st.markdown("<div style='margin:.5rem 0'></div>",unsafe_allow_html=True)
    with st.expander(f"📊 Scores & breakdown · {elapsed}s",expanded=False):
        e1,e2,e3=st.columns(3)
        e1.metric("Company Fit",f"{co_score}/100",fit_lbl)
        e2.metric("Person Score",f"{pe_score}/100",tl(pe_tier))
        e3.metric("Purchase Timing",f"{sig_tot}/100",urg_str(sig_lbl))
        st.markdown("---")
        L,R=st.columns(2)
        with L:
            st.markdown("**Company**")
            for k,lbl,mx in [("industry_fit","Industry (max 40)",40),("company_size","Size (max 25)",25),("geography","Geography (max 20)",20),("physical_site_risk","Risk (max 15)",15)]:
                v=co.get("score_breakdown",{}).get(k,0); ca,cb=st.columns([4,1])
                ca.caption(lbl); ca.progress(v/mx if mx else 0)
                cb.markdown(f"<p style='font-weight:700;color:#F9FAFB;margin-top:18px'>{v}</p>",unsafe_allow_html=True)
        with R:
            st.markdown("**Person**")
            for k,lbl,mx in [("decision_authority","Authority (max 50)",50),("seniority","Seniority (max 30)",30),("engagement_signal","Signal (max 20)",20)]:
                v=pe.get("score_breakdown",{}).get(k,0); ca,cb=st.columns([4,1])
                ca.caption(lbl); ca.progress(v/mx if mx else 0)
                cb.markdown(f"<p style='font-weight:700;color:#F9FAFB;margin-top:18px'>{v}</p>",unsafe_allow_html=True)
        if conf.get("data_notes"): st.caption(conf["data_notes"])
        with st.expander("Raw JSON"): st.json(r)
else:
    st.markdown('<div class="empty"><p style="font-size:2rem;margin:0">🦺</p><p style="font-size:1rem;font-weight:700;color:#F9FAFB;margin:8px 0 3px">Paste an inbound email. Get a decision.</p><p style="font-size:.79rem;color:#4B5563;margin:0">Enter details above or pick a sample lead from the sidebar.</p></div>',unsafe_allow_html=True)
