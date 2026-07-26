"""
Buddywise Lead Intelligence — Knowledge Base
All Buddywise-specific domain knowledge encoded for the AI engine.
"""

# ── BUDDYWISE COMPLETE PRODUCT DESCRIPTION ─────────────────────────────────────
BUDDYWISE_DESCRIPTION = """
COMPANY OVERVIEW:
Buddywise is an AI-powered workplace safety platform founded in 2020 by:
- Lamin Faye (CEO): former VP of Safety and Director of Digitalisation at Vattenfall (Swedish energy giant). Studied computer vision at Singularity University in 2018.
- Yigit Arin (CTO): technology professional and co-founder.

Headquarters: Stockholm, Sweden. Additional office: Berlin, Germany.
Funding: €4.6M raised. Backed by Kvanted, J12, Aligned, and Antler.
Key angel investors: Hans Stråberg (Chair of Atlas Copco and SKF), Hans-Olov Blom (founder of Ramudden Global), Eric Quidenus-Wahlforss (founder of SoundCloud).

CURRENT ACTIVE MARKETS:
Sweden, Finland, Latvia, Poland — expanding across Europe with Germany as key growth market.

WHAT BUDDYWISE DOES:
Buddywise connects to EXISTING CCTV cameras at industrial sites via the "Buddy Box" (an edge computing device). The AI analyses camera feeds 24/7 in real-time to detect safety violations BEFORE accidents happen. No wearables. No new hardware required in most cases.

DETECTION CAPABILITIES:
1. PPE Compliance: Hard hats, safety vests, safety gloves, goggles, steel-toe boots
2. Zone Control: Restricted area monitoring, perimeter breach alerts, exclusion zones
3. Vehicle Safety: Forklift speed violations, vehicle-pedestrian proximity, near-miss events
4. Person Down: Fall detection, worker collapse, health emergencies requiring immediate response
5. Housekeeping: Tools/objects in walkways, slip/trip hazards, obstruction detection
6. Near-Miss Detection: Early warning system before accidents escalate
7. Behaviour Monitoring: Unsafe acts, distraction detection, procedural non-compliance

BUSINESS MODEL:
- SaaS subscription (annual contracts)
- Proof of concept at one site → expand to all sites
- Integrates with existing safety management systems
- White-label options available

KEY VALUE PROPOSITIONS:
1. Prevention not reaction — detect risks before accidents happen
2. 24/7 automated monitoring replacing manual safety walks
3. Reduce workplace insurance costs through documented safety improvements
4. GDPR-compliant — designed specifically for European regulatory environment
5. ROI: average EU workplace accident costs €30,000–€100,000+
6. Uses existing cameras — low implementation friction
7. Real-time configurable alerts to right people via push notification

REGULATORY CONTEXT:
- EU EHS regulations are tightening (ESRS, EU-OSHA reporting requirements)
- DGUV (German statutory accident insurance) audit requirements
- UK HSE compliance requirements
- ISO 45001 occupational health & safety standard
- Companies with >250 employees face mandatory CSRD/ESG safety reporting from 2025

IDEAL CUSTOMER PROFILE:
- 200+ workers at physical industrial sites
- Active EHS function or strong compliance pressure
- Existing CCTV infrastructure (or willing to install cameras)
- European operations, especially DACH and Nordics
- High physical risk environment (machinery, chemicals, heights, vehicles)
- Decision maker: CSO, VP EHS, COO, Plant Manager, CEO (smaller companies)
"""

# ── INDUSTRY TIERS ─────────────────────────────────────────────────────────────
INDUSTRY_SCORING = {
    "TIER_1": {
        "max_score": 40,
        "default_score": 38,
        "label": "Perfect Fit — Core Market",
        "keywords": [
            "chemical", "petrochemical", "oil", "gas", "refinery",
            "heavy manufacturing", "machinery", "machine tools", "machine tool",
            "automotive", "automobile", "car manufacturing", "vehicle manufacturing",
            "aerospace", "defence", "defense", "aviation manufacturing",
            "steel", "metal fabrication", "metallurgy", "aluminium", "aluminum",
            "mining", "extraction", "quarrying", "drilling",
            "pulp", "paper", "forestry", "lumber",
            "energy", "power generation", "nuclear", "power plant",
            "shipbuilding", "marine", "offshore",
            "semiconductor", "electronics manufacturing", "printed circuit",
            "industrial equipment", "heavy equipment", "crane",
            "port", "terminal", "dock",
            "infrastructure", "civil engineering", "bridge", "tunnel",
            "cement", "concrete", "building materials",
        ],
        "description": "Proven Buddywise market. High physical risk, existing cameras, regulatory pressure."
    },
    "TIER_2": {
        "max_score": 32,
        "default_score": 29,
        "label": "High Fit — Strong Secondary Market",
        "keywords": [
            "food manufacturing", "food production", "beverage manufacturing",
            "food and beverage production", "dairy", "brewery", "winery production",
            "pharmaceutical manufacturing", "pharma manufacturing", "drug manufacturing",
            "medical device manufacturing", "biotech manufacturing",
            "waste management", "recycling", "waste treatment",
            "water treatment", "sewage treatment", "utilities",
            "logistics", "warehousing", "distribution center", "fulfillment",
            "construction", "building construction", "general contractor",
            "agriculture scale", "agribusiness", "farm equipment",
            "glass manufacturing", "ceramics", "rubber",
            "printing", "packaging manufacturing",
            "textile manufacturing", "garment manufacturing",
        ],
        "description": "Physical operations with meaningful safety risk. Good product fit."
    },
    "TIER_3": {
        "max_score": 22,
        "default_score": 18,
        "label": "Possible Fit — Mixed Operations",
        "keywords": [
            "courier", "freight", "transportation", "shipping",
            "hospital", "healthcare", "medical", "clinic",
            "large retail", "supermarket", "e-commerce fulfillment",
            "furniture", "wood products", "carpentry",
            "cleaning services", "facilities management",
            "cold storage", "refrigeration",
        ],
        "description": "Some physical risk but not core Buddywise market. Qualify carefully."
    },
    "TIER_4": {
        "max_score": 12,
        "default_score": 8,
        "label": "Weak Fit — Limited Relevance",
        "keywords": [
            "restaurant", "food service", "cafe", "catering",
            "retail", "fashion", "clothing store",
            "hotel", "hospitality", "tourism",
            "media", "entertainment", "advertising", "marketing agency",
            "education", "university", "school",
            "healthcare services", "dental", "pharmacy retail",
            "real estate", "property",
        ],
        "description": "Minimal physical industrial risk. Unlikely to see ROI from Buddywise."
    },
    "TIER_5": {
        "max_score": 4,
        "default_score": 2,
        "label": "Not a Fit — No Industrial Operations",
        "keywords": [
            "software", "saas", "technology company", "app development",
            "fintech", "banking", "finance", "investment", "insurance", "hedge fund",
            "consulting", "professional services", "law firm", "accounting",
            "telecommunications", "internet services",
            "social media", "digital marketing",
        ],
        "description": "No physical industrial operations. Not a Buddywise prospect."
    }
}

# ── PERSON ROLE SCORING ─────────────────────────────────────────────────────────
PERSON_ROLE_SCORING = {
    "decision_authority": {
        # EHS/Safety Champions — perfect buyers
        "Chief Safety Officer": 50,
        "CSO": 50,
        "VP EHS": 50,
        "VP Environment Health Safety": 50,
        "VP Health Safety Environment": 50,
        "Head of EHS": 50,
        "Head of Safety": 50,
        "Director of Safety": 50,
        "EHS Director": 50,
        "HSE Director": 50,
        # Operations Champions
        "Chief Operations Officer": 47,
        "COO": 47,
        "VP Operations": 47,
        "VP Manufacturing": 47,
        "Operations Director": 45,
        "Plant Manager": 44,
        "Facility Director": 44,
        "Site Manager": 44,
        "Manufacturing Director": 44,
        # C-Suite (strategic, can open doors)
        "Chief Executive Officer": 42,
        "CEO": 42,
        "President": 42,
        "Managing Director": 42,
        "Chairman": 38,
        # Finance (approves budget)
        "Chief Financial Officer": 35,
        "CFO": 35,
        "VP Finance": 30,
        # Influencers
        "Safety Manager": 30,
        "EHS Manager": 30,
        "HSE Manager": 30,
        "Operations Manager": 28,
        "Production Manager": 26,
        "HR Director": 22,
        "Head of HR": 22,
        "Sustainability Director": 20,
        "ESG Manager": 20,
        "Engineering Manager": 18,
        "Risk Manager": 20,
        "Compliance Manager": 18,
        # Procurement (signals late-stage)
        "Procurement Manager": 15,
        "Purchasing Manager": 15,
        "Vendor Manager": 15,
        "Strategic Sourcing": 15,
        # Gatekeepers
        "IT Manager": 12,
        "IT Director": 12,
        "CTO": 14,
        "Business Development": 8,
        "Sales Manager": 6,
        "Marketing Manager": 5,
        "Communications": 4,
        # Unknown
        "Unknown": 10,
    }
}

# ── GEOGRAPHY SCORING ───────────────────────────────────────────────────────────
GEOGRAPHY_SCORING = {
    "DACH": {
        "score": 20,
        "countries": ["Germany", "Austria", "Switzerland"],
        "label": "Home market — highest priority"
    },
    "NORDICS": {
        "score": 19,
        "countries": ["Sweden", "Finland", "Norway", "Denmark", "Iceland"],
        "label": "Existing customer base — strong fit"
    },
    "BENELUX_UK": {
        "score": 16,
        "countries": ["United Kingdom", "Netherlands", "Belgium", "Ireland", "Luxembourg"],
        "label": "Active expansion market"
    },
    "CORE_EU": {
        "score": 14,
        "countries": ["France", "Spain", "Italy", "Poland", "Czech Republic", "Hungary", "Portugal"],
        "label": "EU expansion — good fit"
    },
    "REST_EU": {
        "score": 11,
        "countries": ["Romania", "Bulgaria", "Croatia", "Slovakia", "Slovenia", "Greece", "Latvia", "Lithuania", "Estonia"],
        "label": "Existing deployments (Latvia, Poland)"
    },
    "NORTH_AMERICA": {
        "score": 8,
        "countries": ["United States", "USA", "Canada"],
        "label": "Strategic market — longer sales cycle"
    },
    "APAC": {
        "score": 5,
        "countries": ["Japan", "South Korea", "Australia", "Singapore", "China", "India"],
        "label": "Future market — flag for strategic review"
    },
    "OTHER": {
        "score": 3,
        "countries": [],
        "label": "Outside core markets"
    }
}

# ── BUYING SIGNAL FRAMEWORK ─────────────────────────────────────────────────────
BUYING_SIGNAL_FRAMEWORK = {
    "CRITICAL": {
        "score": 25,
        "signals": [
            {
                "id": "new_leader",
                "name": "New C-Suite or EHS Leader (< 18 months in role)",
                "why": "New leaders audit everything, want quick wins, have political capital for new investments. This is Buddywise's highest-value signal.",
                "detection": "Look for recently appointed CEO, COO, CSO, VP EHS, or Plant Manager"
            },
            {
                "id": "recent_accident",
                "name": "Recent workplace accident or fatality (publicly reported)",
                "why": "Company is under legal/reputational pressure. Urgent need for demonstrable safety improvement.",
                "detection": "Recent news about workplace incidents at this company"
            },
            {
                "id": "new_site",
                "name": "New factory, site expansion, or facility opening",
                "why": "New sites need safety infrastructure from day one. Perfect entry point with greenfield opportunity.",
                "detection": "Recent announcements about new plants, expansion projects, new facilities"
            },
            {
                "id": "safety_hiring",
                "name": "Actively hiring safety or EHS personnel",
                "why": "Signals active safety budget allocation and investment in safety function.",
                "detection": "Company has open EHS/safety roles on LinkedIn or job boards"
            },
            {
                "id": "procurement_contact",
                "name": "Contact is in Procurement",
                "why": "Procurement only gets involved when someone internally has already requested the tool. You may be in final evaluation.",
                "detection": "Email contact is in Purchasing, Procurement, or Vendor Management"
            }
        ]
    },
    "HIGH": {
        "score": 15,
        "signals": [
            {
                "id": "esg_commitment",
                "name": "Published ESG or sustainability report with safety targets",
                "why": "Public commitment creates accountability. They need tools to measure and demonstrate progress.",
                "detection": "Recent ESG report, annual report mentioning safety KPIs, public zero-incident goal"
            },
            {
                "id": "peer_accident",
                "name": "Industry peer had a publicised major accident",
                "why": "Competitive fear. 'If it happened to them, it could happen to us.' Creates urgency.",
                "detection": "Recent high-profile accidents in the same industry sector"
            },
            {
                "id": "regulatory_pressure",
                "name": "Known regulatory compliance cycle or audit upcoming",
                "why": "DGUV audits, EU-OSHA reporting, ISO 45001 certification drives purchase decisions.",
                "detection": "Company in regulated industry with compliance deadlines"
            },
            {
                "id": "ma_activity",
                "name": "Recent merger, acquisition, or restructuring",
                "why": "New management audits all operations including safety. Restructuring often triggers technology investment.",
                "detection": "Recent M&A announcements involving this company"
            },
            {
                "id": "digitisation",
                "name": "Active Industry 4.0 / digitalisation programme",
                "why": "Company is already investing in digital transformation. Safety AI fits naturally.",
                "detection": "Announcements about smart factory, Industry 4.0, digital transformation"
            }
        ]
    },
    "MEDIUM": {
        "score": 8,
        "signals": [
            {
                "id": "investor_connection",
                "name": "Connection to Buddywise investor network",
                "why": "Atlas Copco, Ramudden Global, SoundCloud — warm introduction possible through investor network.",
                "detection": "Company connected to Atlas Copco, Ramudden, SKF ecosystem"
            },
            {
                "id": "cost_reduction",
                "name": "Announced cost reduction or efficiency program",
                "why": "Safety ROI argument becomes easier when company is focused on cost reduction.",
                "detection": "Recent announcements about restructuring, cost-cutting, efficiency"
            },
            {
                "id": "rapid_scaling",
                "name": "Rapid headcount or site growth",
                "why": "More workers = more safety exposure. Growing companies need scalable safety solutions.",
                "detection": "Significant hiring, new markets, rapid expansion"
            }
        ]
    }
}

# ── PRIORITY DECISION MATRIX ────────────────────────────────────────────────────
PRIORITY_MATRIX = {
    "FAST_TRACK": {
        "emoji": "🚀",
        "label": "FAST TRACK",
        "hex_color": "#059669",
        "bg_hex": "#064E3B",
        "condition": "Company ≥ 80 AND Person ≥ 70",
        "action": "Reply within the hour. High-value inbound.",
        "sla": "< 1 hour",
        "description": "Exceptional fit on both dimensions. This lead deserves your immediate attention."
    },
    "PURSUE": {
        "emoji": "🎯",
        "label": "PURSUE",
        "hex_color": "#3B82F6",
        "bg_hex": "#1E3A5F",
        "condition": "Company ≥ 65 AND Person ≥ 50",
        "action": "Prioritise today. Strong prospect with good company fit.",
        "sla": "< 24 hours",
        "description": "Strong fit. Move quickly before competitor does."
    },
    "QUALIFY": {
        "emoji": "🔍",
        "label": "QUALIFY",
        "hex_color": "#D97706",
        "bg_hex": "#451A03",
        "condition": "Company ≥ 40 OR (Company ≥ 65 AND Person < 50)",
        "action": "Gather more information. May be worth pursuing with the right contact.",
        "sla": "< 48 hours",
        "description": "Needs more qualification before investing sales time."
    },
    "NURTURE": {
        "emoji": "🌱",
        "label": "NURTURE",
        "hex_color": "#F97316",
        "bg_hex": "#431407",
        "condition": "Company < 40 AND Person ≥ 70",
        "action": "Good contact, weak company fit. Keep the relationship warm.",
        "sla": "< 1 week",
        "description": "Valuable person in a company that is not an immediate fit. Nurture for future."
    },
    "DEPRIORITISE": {
        "emoji": "📭",
        "label": "DEPRIORITISE",
        "hex_color": "#6B7280",
        "bg_hex": "#1F2937",
        "condition": "Company < 40 AND Person < 50",
        "action": "Low fit on both dimensions. Send polite acknowledgement and move on.",
        "sla": "Best effort",
        "description": "Not a Buddywise prospect at this time."
    }
}

# ── EDGE CASES ──────────────────────────────────────────────────────────────────
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "me.com", "gmx.com", "gmx.de", "gmx.net",
    "web.de", "t-online.de", "freenet.de", "posteo.de",
    "proton.me", "protonmail.com", "pm.me",
    "aol.com", "msn.com", "live.com", "live.de",
}

GENERIC_EMAIL_PREFIXES = {
    "info", "contact", "hello", "hallo", "office", "admin",
    "support", "help", "service", "sales", "marketing",
    "hr", "careers", "jobs", "recruitment", "bewerbung",
    "press", "media", "pr", "news",
    "invoice", "billing", "accounts", "buchhaltung",
    "legal", "compliance",
    "team", "general", "enquiries", "anfrage",
}

# ── SAMPLE LEADS FOR DEMO ───────────────────────────────────────────────────────
SAMPLE_LEADS = [
    {"name": "Markus Kamieth", "email": "markus.kamieth@basf.com", "company": "BASF"},
    {"name": "Miguel López Borrego", "email": "miguel.lopez@thyssenkrupp.com", "company": "thyssenkrupp"},
    {"name": "Tobias Meyer", "email": "tobias.meyer@dhl.com", "company": "DHL Group"},
    {"name": "Juan Santamaría", "email": "juan.santamaria@hochtief.com", "company": "HOCHTIEF"},
    {"name": "Nicola Leibinger-Kammüller", "email": "nicola.leibinger@trumpf.com", "company": "TRUMPF"},
    {"name": "Cecilia Felton", "email": "cecilia.felton@sandvik.com", "company": "Sandvik"},
    {"name": "Lena Hök", "email": "lena.hok@skanska.com", "company": "Skanska"},
]
