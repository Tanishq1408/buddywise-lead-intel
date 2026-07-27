"""Buddywise Knowledge Base"""

BUDDYWISE_DESCRIPTION = """
Buddywise is an AI-powered workplace safety platform (founded 2020, Stockholm/Berlin).
CEO: Lamin Faye (ex-VP Safety Vattenfall). CTO: Yigit Arin. Raised €4.6M.
Detects: PPE violations, zone breaches, vehicle speed, person-down, housekeeping hazards.
Uses EXISTING cameras via "Buddy Box" edge device. GDPR compliant.
Active markets: Sweden, Finland, Latvia, Poland, Germany (expanding).
Ideal customer: 200+ workers, physical industrial sites, European operations, active EHS function.
Key buyers: CSO, VP EHS, COO, Plant Manager, CEO (smaller firms).
"""

PRIORITY_MATRIX = {
    "FAST_TRACK": {"emoji":"🚀","label":"FAST TRACK","hex_color":"#059669","bg_hex":"#064E3B","action":"Reply within the hour.","sla":"< 1 hour","description":"Exceptional fit. Prioritise immediately."},
    "PURSUE":      {"emoji":"🎯","label":"PURSUE",     "hex_color":"#3B82F6","bg_hex":"#1E3A5F","action":"Prioritise today.","sla":"< 24 hours","description":"Strong prospect. Move quickly."},
    "QUALIFY":     {"emoji":"🔍","label":"QUALIFY",    "hex_color":"#D97706","bg_hex":"#451A03","action":"Gather more info.","sla":"< 48 hours","description":"Needs more qualification."},
    "NURTURE":     {"emoji":"🌱","label":"NURTURE",    "hex_color":"#F97316","bg_hex":"#431407","action":"Keep the relationship warm.","sla":"< 1 week","description":"Good contact, weak company."},
    "DEPRIORITISE":{"emoji":"📭","label":"DEPRIORITISE","hex_color":"#6B7280","bg_hex":"#1F2937","action":"Acknowledge and move on.","sla":"Best effort","description":"Low fit on both dimensions."},
}

PERSONAL_EMAIL_DOMAINS = {
    "gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com",
    "me.com","gmx.com","gmx.de","web.de","proton.me","protonmail.com","aol.com",
}

GENERIC_EMAIL_PREFIXES = {
    "info","contact","hello","office","admin","support","sales",
    "marketing","hr","careers","jobs","press","media","team","general",
}

# ── CASE STUDY LEADS ─────────────────────────────────────────────────────────
CASE_STUDY_LEADS = [
    {"name":"Markus Kamieth",           "email":"markus.kamieth@basf.com",          "company":"BASF",         "tag":"🧪 Chemical"},
    {"name":"Miguel López Borrego",     "email":"miguel.lopez@thyssenkrupp.com",     "company":"thyssenkrupp", "tag":"⚙️ Heavy Mfg"},
    {"name":"Tobias Meyer",             "email":"tobias.meyer@dhl.com",              "company":"DHL Group",    "tag":"📦 Logistics"},
    {"name":"Juan Santamaría",          "email":"juan.santamaria@hochtief.com",      "company":"HOCHTIEF",     "tag":"🏗️ Construction"},
    {"name":"Nicola Leibinger-Kammüller","email":"nicola.leibinger@trumpf.com",      "company":"TRUMPF",       "tag":"🔧 Machine Tools"},
    {"name":"Cecilia Felton",           "email":"cecilia.felton@sandvik.com",        "company":"Sandvik",      "tag":"⛏️ Mining/Mfg"},
    {"name":"Lena Hök",                 "email":"lena.hok@skanska.com",              "company":"Skanska",      "tag":"🏗️ Construction"},
]

# ── DIVERSE SHOWCASE LEADS ──────────────────────────────────────────────────
SHOWCASE_LEADS = [
    # FAST TRACK examples
    {"name":"Elon Musk",            "email":"elon.musk@tesla.com",           "company":"Tesla",         "tag":"🚗 Auto Mfg",    "expected":"🚀 FAST TRACK"},
    {"name":"Roland Busch",         "email":"roland.busch@siemens.com",      "company":"Siemens",       "tag":"⚡ Industrial",   "expected":"🚀 FAST TRACK"},
    {"name":"Wael Sawan",           "email":"wael.sawan@shell.com",          "company":"Shell",         "tag":"🛢️ Oil & Gas",   "expected":"🚀 FAST TRACK"},
    # PURSUE examples
    {"name":"Andy Jassy",           "email":"andy.jassy@amazon.com",         "company":"Amazon",        "tag":"📦 Logistics",   "expected":"🎯 PURSUE"},
    {"name":"Mark Schneider",       "email":"mark.schneider@nestle.com",     "company":"Nestlé",        "tag":"🏭 Food Mfg",    "expected":"🎯 PURSUE"},
    # LOW FIT / DEPRIORITISE
    {"name":"Sundar Pichai",        "email":"sundar.pichai@google.com",      "company":"Google",        "tag":"💻 Tech/Software","expected":"📭 DEPRIORITISE"},
    {"name":"Russ Weiner",          "email":"russ.weiner@dominos.com",       "company":"Domino's Pizza","tag":"🍕 Food Service", "expected":"📭 DEPRIORITISE"},
    # Personal email edge case
    {"name":"Unknown Contact",      "email":"unknown.person@gmail.com",      "company":"",              "tag":"📧 Personal Email","expected":"🔍 QUALIFY"},
]

# All leads combined for sidebar
SAMPLE_LEADS = CASE_STUDY_LEADS + SHOWCASE_LEADS
