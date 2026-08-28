import os
import tempfile
import streamlit as st
from pypdf import PdfReader
from src.profile_builder import CandidateProfileBuilder
from src.agents import get_all_personas
from src.debate_engine import DebateEngine
from src.decision_engine import DecisionEngine
from src.gemini_client import GeminiClient

st.set_page_config(
    page_title="HireMind — Multi-Agent AI Interview Panel",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for dark glassmorphism styling
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #cbd5e1; }
    .quote-box { background: rgba(15, 23, 42, 0.7); border-left: 3px solid #14b8a6; padding: 0.6rem 0.8rem; border-radius: 0 0.5rem 0.5rem 0; font-style: italic; font-size: 0.85rem; }
    .metric-box { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 0.75rem; padding: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Ensure benchmark PDFs exist
if not os.path.exists(os.path.join("data", "02_Job_Description.pdf")):
    from generate_pdfs import generate_all_pdfs
    generate_all_pdfs()

gemini_client = GeminiClient()
jd_path = os.path.join("data", "02_Job_Description.pdf")
resume_a_path = os.path.join("data", "03_Resume_A.pdf")
resume_b_path = os.path.join("data", "04_Resume_B.pdf")
transcript_a_path = os.path.join("data", "05_Transcript_A.pdf")
transcript_b_path = os.path.join("data", "06_Transcript_B.pdf")

profile_builder_a = CandidateProfileBuilder(jd_path, resume_a_path, transcript_a_path)
profile_builder_b = CandidateProfileBuilder(jd_path, resume_b_path, transcript_b_path)
decision_engine = DecisionEngine()
debate_engine = DebateEngine(gemini_client)

@st.cache_data
def evaluate_candidate(cid: str):
    pb = profile_builder_a if cid == "A" else profile_builder_b
    profile = pb.build_profile(cid)
    personas = get_all_personas(gemini_client)
    initial_evals = {agent.name: agent.evaluate_independent(profile) for agent in personas}
    debate_data = debate_engine.run_debate(profile, initial_evals)
    final_report = decision_engine.synthesize_decision(profile, initial_evals, debate_data)
    return profile, initial_evals, debate_data, final_report

def evaluate_custom_pdf(uploaded_resume, uploaded_transcript):
    """Dynamically parses and evaluates an uploaded custom PDF resume and transcript."""
    temp_dir = tempfile.mkdtemp()
    res_path = os.path.join(temp_dir, "custom_resume.pdf")
    tr_path = os.path.join(temp_dir, "custom_transcript.pdf")
    
    with open(res_path, "wb") as f:
        f.write(uploaded_resume.read())
        
    if uploaded_transcript:
        with open(tr_path, "wb") as f:
            f.write(uploaded_transcript.read())
    else:
        tr_path = transcript_b_path # fallback transcript
        
    builder = CandidateProfileBuilder(jd_path, res_path, tr_path)
    profile = builder.build_profile("B")
    profile["name"] = uploaded_resume.name.replace(".pdf", "").replace("_", " ").title()
    
    personas = get_all_personas(gemini_client)
    initial_evals = {agent.name: agent.evaluate_independent(profile) for agent in personas}
    debate_data = debate_engine.run_debate(profile, initial_evals)
    final_report = decision_engine.synthesize_decision(profile, initial_evals, debate_data)
    final_report["candidate_name"] = profile["name"]
    
    return profile, initial_evals, debate_data, final_report

st.title("🤖 HireMind: Multi-Agent AI Interview Panel Simulator")
st.caption("Executive hiring panel powered by 4 isolated AI personas, real debate cross-examination, and weighed decision synthesis.")

# Sidebar Candidate Selection & File Upload
st.sidebar.header("Candidate Selector")
candidate_choice = st.sidebar.radio(
    "Select Candidate / Mode:",
    ["Candidate A: Rohan Malhotra", "Candidate B: Maya Lin", "📤 Upload Custom PDF Resume", "📊 Side-by-Side Comparison"]
)

if candidate_choice == "📤 Upload Custom PDF Resume":
    st.sidebar.subheader("Upload Custom PDF")
    custom_resume_file = st.sidebar.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])
    custom_transcript_file = st.sidebar.file_uploader("Upload Interview Transcript (PDF, Optional)", type=["pdf"])

    if custom_resume_file is not None:
        with st.spinner("Parsing uploaded PDF and executing 4-agent panel evaluation..."):
            profile, initial_evals, debate_data, final_report = evaluate_custom_pdf(custom_resume_file, custom_transcript_file)
            
        st.success(f"Successfully evaluated uploaded resume: **{profile['name']}**")
        
        # Hero Metrics Bar
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**Target Candidate:** {profile['name']}")
            st.caption(f"Role: {profile['target_role']}")
        with col2:
            verdict = final_report['final_recommendation']
            color = "🔴" if "REJECT" in verdict else "🟢"
            st.markdown(f"**Panel Verdict:** {color} {verdict}")
        with col3:
            st.markdown(f"**Weighted Score:** {final_report['weighted_score']} / 10")
        with col4:
            st.markdown(f"**Confidence:** {final_report['confidence_level']}%")

        st.divider()

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "1. Isolated Persona Evals",
            "2. Live Debate & Opinion Shifts",
            "3. Weighed Decision Report",
            "4. Evidence Hub & Quotes"
        ])

        with tab1:
            st.subheader("Phase 1: Isolated Independent Evaluations")
            st.caption("Each agent evaluates strictly from its perspective in isolated LLM calls citing exact quotes.")
            cols = st.columns(2)
            idx = 0
            for name, ev in initial_evals.items():
                with cols[idx % 2]:
                    with st.expander(f"**{name}** — Score: {ev['score']}/10 ({ev.get('confidence', 90)}%)", expanded=True):
                        st.write(f"**Verdict:** {ev['verdict']}")
                        st.write(f"*{ev['summary']}*")
                        if ev.get('strengths'):
                            s = ev['strengths'][0]
                            st.markdown(f"<div class='quote-box'><b>Strength:</b> \"{s['quote']}\" ({s.get('source', 'Uploaded Resume')})</div>", unsafe_allow_html=True)
                        if ev.get('concerns'):
                            c = ev['concerns'][0]
                            st.markdown(f"<div class='quote-box'><b>Concern:</b> \"{c['quote']}\" ({c.get('source', 'Uploaded Resume')})</div>", unsafe_allow_html=True)
                idx += 1

        with tab2:
            st.subheader("Phase 2: Multi-Agent Debate & Opinion Changes")
            st.markdown("### 📈 Opinion Change Delta Log")
            if not debate_data['opinion_deltas']:
                st.info("No score changes occurred during debate.")
            else:
                for d in debate_data['opinion_deltas']:
                    st.warning(f"**{d['agent_name']}**: {d['before_score']}/10 ➔ {d['after_score']}/10 | Triggered by **{d['trigger_agent']}** | Reason: {d['reason']}")

            st.markdown("### 💬 Panel Debate Transcript")
            for turn in debate_data['debate_transcript']:
                is_shift = turn['stance'] == 'opinion_change'
                icon = "⚡" if is_shift else "💬"
                st.markdown(f"**{icon} {turn['speaker']}** ➔ *{turn['target']}* (Round {turn['round']}):")
                st.write(turn['text'])
                if turn.get('quote_cited'):
                    st.markdown(f"<div class='quote-box'>Evidence: \"{turn['quote_cited']}\"</div>", unsafe_allow_html=True)
                st.divider()

        with tab3:
            st.subheader("Phase 3: Weighed Decision Report")
            st.markdown(f"### Verdict: {final_report['final_recommendation']} ({final_report['weighted_score']}/10)")
            st.write(final_report['executive_summary'])

            col_s, col_c = st.columns(2)
            with col_s:
                st.markdown("#### ✅ Verified Key Strengths")
                for s in final_report['strengths']:
                    st.write(f"- {s}")
            with col_c:
                st.markdown("#### ⚠️ Critical Red Flags")
                for c in final_report['concerns']:
                    st.write(f"- {c}")

        with tab4:
            st.subheader("Extracted Transcript Evidence & Quotes")
            for q in profile['key_transcript_quotes']:
                st.markdown(f"**{q['topic']}**")
                st.markdown(f"<div class='quote-box'>\"{q['quote']}\"</div>", unsafe_allow_html=True)
                st.caption(f"Context: {q['context']}")
                st.divider()
    else:
        st.info("👈 Please drag and drop a candidate PDF resume file in the sidebar to run custom AI panel evaluation!")

elif candidate_choice == "📊 Side-by-Side Comparison":
    prof_a, ev_a, deb_a, rep_a = evaluate_candidate("A")
    prof_b, ev_b, deb_b, rep_b = evaluate_candidate("B")
    ranking = decision_engine.rank_candidates(rep_a, rep_b)

    st.subheader(f"🏆 Top Candidate Selected: {ranking['top_candidate']} ({ranking['score_gap']} pts gap)")
    st.info(ranking['recommendation_summary'])

    st.subheader("Side-by-Side Evaluation Matrix")
    st.table(ranking['comparison_matrix'])

else:
    cid = "A" if "Rohan" in candidate_choice else "B"
    profile, initial_evals, debate_data, final_report = evaluate_candidate(cid)

    # Hero Metrics Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Target Candidate:** {profile['name']}")
        st.caption(f"Role: {profile['target_role']}")
    with col2:
        verdict = final_report['final_recommendation']
        color = "🔴" if "REJECT" in verdict else "🟢"
        st.markdown(f"**Panel Verdict:** {color} {verdict}")
    with col3:
        st.markdown(f"**Weighted Score:** {final_report['weighted_score']} / 10")
    with col4:
        st.markdown(f"**Confidence:** {final_report['confidence_level']}%")

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Isolated Persona Evals",
        "2. Live Debate & Opinion Shifts",
        "3. Weighed Decision Report",
        "4. Evidence Hub & Quotes"
    ])

    with tab1:
        st.subheader("Phase 1: Isolated Independent Evaluations")
        st.caption("Each agent evaluates strictly from its perspective in isolated LLM calls citing exact quotes.")
        
        cols = st.columns(2)
        idx = 0
        for name, ev in initial_evals.items():
            with cols[idx % 2]:
                with st.expander(f"**{name}** — Score: {ev['score']}/10 ({ev.get('confidence', 90)}%)", expanded=True):
                    st.write(f"**Verdict:** {ev['verdict']}")
                    st.write(f"*{ev['summary']}*")
                    if ev.get('strengths'):
                        s = ev['strengths'][0]
                        st.markdown(f"<div class='quote-box'><b>Strength:</b> \"{s['quote']}\" ({s['source']})</div>", unsafe_allow_html=True)
                    if ev.get('concerns'):
                        c = ev['concerns'][0]
                        st.markdown(f"<div class='quote-box'><b>Concern:</b> \"{c['quote']}\" ({c['source']})</div>", unsafe_allow_html=True)
            idx += 1

    with tab2:
        st.subheader("Phase 2: Multi-Agent Debate & Opinion Changes")
        
        st.markdown("### 📈 Opinion Change Delta Log")
        if not debate_data['opinion_deltas']:
            st.info("No score changes occurred during debate.")
        else:
            for d in debate_data['opinion_deltas']:
                st.warning(f"**{d['agent_name']}**: {d['before_score']}/10 ➔ {d['after_score']}/10 | Triggered by **{d['trigger_agent']}** | Reason: {d['reason']}")

        st.markdown("### 💬 Panel Debate Transcript")
        for turn in debate_data['debate_transcript']:
            is_shift = turn['stance'] == 'opinion_change'
            icon = "⚡" if is_shift else "💬"
            st.markdown(f"**{icon} {turn['speaker']}** ➔ *{turn['target']}* (Round {turn['round']}):")
            st.write(turn['text'])
            if turn.get('quote_cited'):
                st.markdown(f"<div class='quote-box'>Evidence: \"{turn['quote_cited']}\"</div>", unsafe_allow_html=True)
            st.divider()

    with tab3:
        st.subheader("Phase 3: Weighed Decision Report")
        st.markdown(f"### Verdict: {final_report['final_recommendation']} ({final_report['weighted_score']}/10)")
        st.write(final_report['executive_summary'])

        col_s, col_c = st.columns(2)
        with col_s:
            st.markdown("#### ✅ Verified Key Strengths")
            for s in final_report['strengths']:
                st.write(f"- {s}")
        with col_c:
            st.markdown("#### ⚠️ Critical Red Flags")
            for c in final_report['concerns']:
                st.write(f"- {c}")

    with tab4:
        st.subheader("Extracted Transcript Evidence & Quotes")
        for q in profile['key_transcript_quotes']:
            st.markdown(f"**{q['topic']}**")
            st.markdown(f"<div class='quote-box'>\"{q['quote']}\"</div>", unsafe_allow_html=True)
            st.caption(f"Context: {q['context']}")
            st.divider()
