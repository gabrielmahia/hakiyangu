# Copyright (c) 2026 Gabriel Mahia / AI Kung Fu LLC. MIT License.
# haki-debate-ai — Constitutional Rights Multi-Agent Debate
# Research basis:
#   Liang et al. (2023) "Encouraging Divergent Thinking in LLMs through Debate" arXiv:2305.19118
#   "Right to AI" (2025) arXiv:2501.17899 — AI as civil right for underserved communities
#   "AI Diffusion in Low Resource Language Countries" arXiv:2511.02752 (2025)
# First in East Africa: multi-agent adversarial debate for civic rights education
# =============================================================================

import streamlit as st
import urllib.request
import json
import time as _time

st.set_page_config(
    page_title="Hakiyangu — Haki Debate AI — Haki za Katiba",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  .stApp { background: #1a0a2e; }
  .title { font-size:1.5rem; font-weight:800; color:#ce93d8; text-align:center; }
  .sub   { font-size:0.82rem; color:#9c27b0; text-align:center; margin-bottom:1rem; }
  .gov-card  { background:#0d1b2a; border:1px solid #1565c0; border-radius:8px; padding:12px; margin:6px 0; }
  .cit-card  { background:#1a0a2e; border:1px solid #6a1b9a; border-radius:8px; padding:12px; margin:6px 0; }
  .synthesis { background:#0d2b0d; border:1px solid #2e7d32; border-radius:8px; padding:12px; margin:6px 0; }
  .demo-tag { background:#e65100; color:#fff; font-size:0.6rem; padding:2px 6px; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚖️ Hakiyangu — Haki Debate AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub">Mjadala wa AI kuhusu haki za katiba — serikali vs raia &nbsp;'
    '<span class="demo-tag">DEMO</span></div>',
    unsafe_allow_html=True
)

# ── API Key ───────────────────────────────────────────────────────────────────
API_KEY = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.warning(
        "⚠️ **Huduma hii bado haijaungwa.** Rudi baadaye.\n\n"
        "_This service is not yet configured in this demo. Check back soon._"
    )
    st.stop()

# ── Debate topics ─────────────────────────────────────────────────────────────
TOPICS = {
    "Land Rights (Article 40)": {
        "sw": "Haki za Ardhi (Kifungu cha 40)",
        "context": "Kenya Constitution Article 40: right to property. Government can acquire land for public purposes with fair compensation.",
        "government_angle": "Article 40(3): state has power to acquire land for public benefit. Compulsory acquisition is constitutional when compensation is paid.",
        "citizen_angle": "Article 40(1): every person has right to acquire and own property. Article 40(2)(a): no one may be arbitrarily deprived of property.",
    },
    "Right to Healthcare (Article 43)": {
        "sw": "Haki ya Afya (Kifungu cha 43)",
        "context": "Kenya Constitution Article 43: every person has the right to the highest attainable standard of health.",
        "government_angle": "Article 43(2): state must achieve progressive realization of economic and social rights — subject to available resources.",
        "citizen_angle": "Article 43(1)(a): every person has right to health care services including reproductive health care. This is immediate, not progressive.",
    },
    "Digital Rights and Privacy (Article 31)": {
        "sw": "Haki za Kidijitali na Faragha (Kifungu cha 31)",
        "context": "Kenya Constitution Article 31: right to privacy. Kenya Data Protection Act 2019.",
        "government_angle": "Article 31(a): right to privacy of persons is balanced against legitimate government security interests and national security.",
        "citizen_angle": "Article 31(c)-(d): no person may require another to reveal personal communications or have information relating to their family shared without consent.",
    },
    "Freedom of Expression (Article 33)": {
        "sw": "Uhuru wa Kujieleza (Kifungu cha 33)",
        "context": "Kenya Constitution Article 33: freedom of expression including seeking, receiving, and imparting information.",
        "government_angle": "Article 33(2): freedom of expression does not extend to propaganda for war, incitement to violence, advocacy of hatred, or vilification of others.",
        "citizen_angle": "Article 33(1)(a)-(d): every person has the right to freedom of expression in any medium. This includes criticism of government.",
    },
    "Labor Rights (Article 41)": {
        "sw": "Haki za Kazi (Kifungu cha 41)",
        "context": "Kenya Constitution Article 41: fair labor practices, right to form unions, right to strike.",
        "government_angle": "Article 41(4): national legislation may limit strikes in essential services such as water, sanitation, transport, healthcare.",
        "citizen_angle": "Article 41(2)(d): every worker has the right to strike. Essential service limits must be proportionate and narrowly defined.",
    },
}

# ── UI ────────────────────────────────────────────────────────────────────────
topic_key = st.selectbox("📋 Chagua haki ya kujadili (Select a right to debate)",
                          list(TOPICS.keys()))
topic = TOPICS[topic_key]
user_question = st.text_area(
    f"✍️ Swali lako kuhusu {topic['sw']} (Your specific question)",
    placeholder=f"Mfano: Je, serikali inaweza kunifukuza ardhi yangu bila idhini yangu? / Example: Can the government take my land without my consent?",
    height=80
)
lang = st.radio("🌐 Lugha ya majibu (Response language)", ["Swahili", "English", "Both"], horizontal=True)

if st.button("⚔️ Anza Mjadala (Start Debate)", type="primary") and user_question.strip():
    with st.spinner("Watoa hoja wanaandaa hoja... / Preparing arguments..."):
        def call_gemini(system_role, user_msg):
            payload = {
                "model": "gemini-2.0-flash",
                "contents": [{"parts": [{"text": user_msg}]}],
                "system_instruction": {"parts": [{"text": system_role}]},
                "generation_config": {"temperature": 0.7, "max_output_tokens": 400}
            }
            for _ver in ("v1", "v1beta"):
                _url = f"https://generativelanguage.googleapis.com/{_ver}/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                try:
                    _req = urllib.request.Request(_url, data=json.dumps(payload).encode(),
                                                  method="POST", headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(_req, timeout=30) as _r:
                        resp = json.loads(_r.read())
                    return resp["candidates"][0]["content"]["parts"][0]["text"]
                except urllib.error.HTTPError as _he:
                    if _ver == "v1beta":
                        return f"⚠️ Hitilafu ya API ({_he.code}). Jaribu tena baadaye. / API error ({_he.code}). Please try again later."
                    continue
            return "⚠️ Huduma haipatikani sasa hivi. / Service temporarily unavailable."

        lang_instr = {
            "Swahili": "Respond entirely in Swahili (Kiswahili). Use simple language a farmer or market trader would understand.",
            "English": "Respond in clear English. Use plain language accessible to someone with basic education.",
            "Both": "Respond first in Swahili, then provide an English translation. Keep both versions concise."
        }[lang]

        ctx = topic["context"]
        gov_angle = topic["government_angle"]
        cit_angle = topic["citizen_angle"]
        question = user_question.strip()

        # Government position
        gov_system = f"""You are a Senior Government Legal Officer defending the Kenya government position on constitutional rights.
You represent the government's lawful interests fairly and accurately.
{lang_instr}
Context: {ctx}
Government position basis: {gov_angle}
Be factual. Cite the actual constitutional articles. Be respectful of citizen rights even while defending government position.
Keep response under 200 words."""

        try:
            gov_response = call_gemini(gov_system,
                f"Citizen question: '{question}'\n\nExplain the government's position on this, citing the Kenya Constitution.")
        except Exception as _e:
            gov_response = f"⚠️ Hitilafu: {str(_e)[:60]}"

        _time.sleep(0.5)

        # Citizen/rights position
        cit_system = f"""You are a Human Rights Advocate defending citizen rights under the Kenya Constitution.
You represent citizens' constitutional rights fairly and accurately.
{lang_instr}
Context: {ctx}
Citizen rights basis: {cit_angle}
Be factual. Cite the actual constitutional articles. Acknowledge government has some valid interests while defending citizen rights strongly.
Keep response under 200 words."""

        try:
            cit_response = call_gemini(cit_system,
                f"Citizen question: '{question}'\n\nExplain the citizen's constitutional rights here, citing the Kenya Constitution.")
        except Exception as _e:
            cit_response = f"⚠️ Hitilafu: {str(_e)[:60]}"

        _time.sleep(0.5)

        # Synthesis
        synth_system = f"""You are an independent Constitutional Law Lecturer at University of Nairobi.
You synthesize both sides of a constitutional debate fairly.
{lang_instr}
You have heard both sides argue. Now provide balanced, practical guidance to help a citizen understand their rights.
Focus on: what can the citizen do, what their strongest legal protections are, and when to seek formal legal help.
Keep response under 150 words."""

        try:
            synthesis = call_gemini(synth_system,
                f"Citizen question: '{question}'\n\nGovernment argued: {gov_response[:300]}\n\nRights advocate argued: {cit_response[:300]}\n\nProvide balanced synthesis.")
        except Exception as _e:
            synthesis = f"⚠️ Hitilafu ya muhtasari: {str(_e)[:60]}"

    # Display
    st.markdown("---")
    st.markdown(f"**🗂️ {topic_key} | {topic['sw']}**")

    st.markdown("#### 🏛️ Msimamo wa Serikali (Government Position)")
    st.markdown(f'<div class="gov-card">{gov_response}</div>', unsafe_allow_html=True)

    st.markdown("#### 👤 Haki za Raia (Citizen Rights)")
    st.markdown(f'<div class="cit-card">{cit_response}</div>', unsafe_allow_html=True)

    st.markdown("#### ⚖️ Muhtasari wa Haki (Balanced Synthesis)")
    st.markdown(f'<div class="synthesis">{synthesis}</div>', unsafe_allow_html=True)

    st.warning(
        "⚠️ **Hii ni elimu tu — si ushauri wa kisheria.** / "
        "This is educational only — not legal advice. "
        "For legal help: Kenya National Human Rights Commission (nhrc.or.ke) or "
        "Federation of Women Lawyers (FIDA Kenya)."
    )
    st.caption("Research basis: Liang et al. (2023) arXiv:2305.19118 — Multi-agent debate improves reasoning accuracy")
