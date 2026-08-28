// HireMind Frontend Application Logic

let currentCandidateId = "A";
let currentData = null;
let currentTab = "tab-evals";
let isVoicePlaying = false;
let speechUtterance = null;

document.addEventListener("DOMContentLoaded", () => {
    loadCandidateData("A");
});

async function loadCandidateData(cid) {
    currentCandidateId = cid;
    stopVoiceDebate();

    // Toggle button active state
    document.getElementById("btn-cand-a").className = cid === 'A' 
        ? "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 bg-teal-600 text-white shadow"
        : "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800";
        
    document.getElementById("btn-cand-b").className = cid === 'B' 
        ? "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 bg-teal-600 text-white shadow"
        : "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800";

    document.getElementById("btn-comparison").className = "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 text-indigo-400 hover:bg-indigo-950/50";

    document.getElementById("hero-summary-section").style.display = "grid";
    document.getElementById("tabs-container").style.display = "flex";
    document.getElementById("section-comparison").classList.add("hidden");
    
    showCurrentTab();

    try {
        const resp = await fetch(`/api/candidate/${cid}`);
        currentData = await resp.json();
        renderDashboard(currentData);
    } catch (err) {
        console.error("Error fetching candidate data:", err);
    }
}

function renderDashboard(data) {
    const report = data.final_report;
    const profile = data.profile;

    // Render Hero Cards
    document.getElementById("hero-target-role").innerText = profile.target_role;
    document.getElementById("hero-company").innerText = `${profile.name} — ${profile.company}`;
    
    const badge = document.getElementById("hero-verdict-badge");
    badge.innerText = report.final_recommendation;
    if (report.final_recommendation.includes("REJECT")) {
        badge.className = "px-3.5 py-1.5 rounded-xl text-sm font-extrabold uppercase tracking-wide bg-rose-500/20 text-rose-400 border border-rose-500/30";
    } else {
        badge.className = "px-3.5 py-1.5 rounded-xl text-sm font-extrabold uppercase tracking-wide bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    }

    document.getElementById("hero-score").innerText = report.weighted_score;
    document.getElementById("hero-confidence").innerText = `${report.confidence_level}%`;

    // Render Tab 1: Independent Persona Evaluations
    renderPersonaCards(data.initial_evals);

    // Render Tab 2: Live Debate & Opinion Changes
    renderDebateSection(data.debate_data);

    // Render Tab 3: Decision & Report
    renderDecisionReport(report);

    // Render Tab 4: Evidence & Quotes
    renderQuotes(profile.key_transcript_quotes);
}

function renderPersonaCards(evals) {
    const container = document.getElementById("persona-cards-grid");
    container.innerHTML = "";

    const accentClasses = {
        "Technical Agent": "persona-tech",
        "HR / Culture Agent": "persona-hr",
        "Hiring Manager Agent": "persona-hm",
        "Skeptic Agent": "persona-skeptic"
    };

    const icons = {
        "Technical Agent": "fa-microchip text-blue-400",
        "HR / Culture Agent": "fa-heart-pulse text-pink-400",
        "Hiring Manager Agent": "fa-briefcase text-emerald-400",
        "Skeptic Agent": "fa-user-ninja text-amber-400"
    };

    for (const [name, ev] of Object.entries(evals)) {
        const card = document.createElement("div");
        card.className = `glass-card rounded-2xl p-5 flex flex-col gap-4 ${accentClasses[name] || ''}`;

        let strengthsHtml = (ev.strengths || []).map(s => `
            <div class="text-xs text-slate-300">
                <span class="font-semibold text-emerald-400">&bull; ${s.point}</span>
                <div class="quote-box mt-1 text-slate-400 text-[11px]">"${s.quote}" <span class="text-teal-400/80">(${s.source})</span></div>
            </div>
        `).join('');

        let concernsHtml = (ev.concerns || []).map(c => `
            <div class="text-xs text-slate-300">
                <span class="font-semibold text-rose-400">&bull; ${c.point}</span>
                <div class="quote-box mt-1 text-slate-400 text-[11px] border-l-rose-500">"${c.quote}" <span class="text-rose-400/80">(${c.source})</span></div>
            </div>
        `).join('');

        card.innerHTML = `
            <div class="flex items-center justify-between border-b border-slate-700/60 pb-3">
                <div class="flex items-center gap-3">
                    <i class="fa-solid ${icons[name] || 'fa-user'} text-lg"></i>
                    <div>
                        <h3 class="text-sm font-bold text-white">${name}</h3>
                        <span class="text-[11px] text-slate-400">${ev.role}</span>
                    </div>
                </div>
                <div class="text-right">
                    <span class="text-lg font-black text-white">${ev.score}</span><span class="text-xs text-slate-400">/10</span>
                    <div class="text-[10px] text-slate-400">${ev.confidence}% Confidence</div>
                </div>
            </div>
            <div class="text-xs text-slate-300 italic bg-slate-900/40 p-2.5 rounded-lg border border-slate-800">
                <strong>Verdict Stance:</strong> ${ev.verdict} — ${ev.summary}
            </div>
            <div class="flex flex-col gap-3 mt-1">
                ${strengthsHtml ? `<div class="flex flex-col gap-1.5"><span class="text-[11px] font-bold uppercase text-emerald-400">Key Strengths Cited</span>${strengthsHtml}</div>` : ''}
                ${concernsHtml ? `<div class="flex flex-col gap-1.5"><span class="text-[11px] font-bold uppercase text-rose-400">Key Concerns Cited</span>${concernsHtml}</div>` : ''}
            </div>
        `;
        container.appendChild(card);
    }
}

function renderDebateSection(debateData) {
    // Render Opinion Deltas
    const deltasContainer = document.getElementById("opinion-deltas-container");
    deltasContainer.innerHTML = "";

    if (!debateData.opinion_deltas || debateData.opinion_deltas.length === 0) {
        deltasContainer.innerHTML = `<div class="text-xs text-slate-400 italic">No score shifts occurred during debate (Panel was fully aligned).</div>`;
    } else {
        debateData.opinion_deltas.forEach(d => {
            const isDowngrade = d.after_score < d.before_score;
            const badgeColor = isDowngrade ? "bg-rose-500/20 text-rose-400 border-rose-500/30" : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
            
            const div = document.createElement("div");
            div.className = "bg-slate-900/60 border border-slate-800 rounded-xl p-3 flex flex-col md:flex-row items-start md:items-center justify-between gap-3";
            div.innerHTML = `
                <div class="flex items-center gap-3">
                    <span class="px-2.5 py-1 rounded-lg text-xs font-bold border ${badgeColor}">
                        ${d.agent_name}: ${d.before_score}/10 &rarr; ${d.after_score}/10
                    </span>
                    <span class="text-xs font-semibold text-slate-300">Triggered by: <strong class="text-indigo-400">${d.trigger_agent}</strong></span>
                </div>
                <div class="text-xs text-slate-400 max-w-xl">
                    <strong>Reason:</strong> ${d.reason}
                </div>
            `;
            deltasContainer.appendChild(div);
        });
    }

    // Render Debate Feed
    const feed = document.getElementById("debate-feed");
    feed.innerHTML = "";

    const avatars = {
        "Technical Agent": "bg-blue-600/30 text-blue-400 border-blue-500/40",
        "HR / Culture Agent": "bg-pink-600/30 text-pink-400 border-pink-500/40",
        "Hiring Manager Agent": "bg-emerald-600/30 text-emerald-400 border-emerald-500/40",
        "Skeptic Agent": "bg-amber-600/30 text-amber-400 border-amber-500/40"
    };

    debateData.debate_transcript.forEach((t, idx) => {
        const bubble = document.createElement("div");
        const isChange = t.stance === "opinion_change";
        bubble.className = `debate-bubble flex flex-col gap-2 ${isChange ? 'opinion_change' : ''}`;
        bubble.id = `debate-turn-${idx}`;

        const avStyle = avatars[t.speaker] || "bg-slate-800 text-white";
        const stanceBadge = isChange 
            ? `<span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-indigo-500 text-white">OPINION SHIFT</span>`
            : `<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-400">Round ${t.round}</span>`;

        bubble.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <span class="w-7 h-7 rounded-full border flex items-center justify-center text-xs font-bold ${avStyle}">
                        ${t.speaker[0]}
                    </span>
                    <span class="text-xs font-bold text-white">${t.speaker}</span>
                    <span class="text-xs text-slate-400">&rarr; ${t.target}</span>
                </div>
                ${stanceBadge}
            </div>
            <p class="text-xs text-slate-200 leading-relaxed font-sans">${t.text}</p>
            ${t.quote_cited ? `<div class="quote-box text-[11px] text-slate-400">Cited Evidence: "${t.quote_cited}"</div>` : ''}
        `;
        feed.appendChild(bubble);
    });
}

function renderDecisionReport(report) {
    document.getElementById("report-candidate-name").innerText = `${report.candidate_name} — Evaluation`;
    document.getElementById("report-recommendation").innerText = report.final_recommendation;
    document.getElementById("report-score-box").innerText = report.weighted_score;
    document.getElementById("report-executive-summary").innerText = report.executive_summary;

    const strList = document.getElementById("report-strengths");
    strList.innerHTML = report.strengths.map(s => `<li>${s}</li>`).join('');

    const conList = document.getElementById("report-concerns");
    conList.innerHTML = report.concerns.map(c => `<li>${c}</li>`).join('');
}

function renderQuotes(quotes) {
    const list = document.getElementById("quotes-list");
    list.innerHTML = "";

    quotes.forEach(q => {
        const card = document.createElement("div");
        card.className = "bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col gap-2";
        card.innerHTML = `
            <div class="flex items-center justify-between text-xs">
                <span class="font-bold text-teal-400 uppercase tracking-wider">${q.topic}</span>
            </div>
            <div class="quote-box text-xs text-slate-200">"${q.quote}"</div>
            <p class="text-[11px] text-slate-400 italic">Context: ${q.context}</p>
        `;
        list.appendChild(card);
    });
}

async function selectComparison() {
    stopVoiceDebate();
    document.getElementById("btn-cand-a").className = "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800";
    document.getElementById("btn-cand-b").className = "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800";
    document.getElementById("btn-comparison").className = "px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 bg-indigo-600 text-white shadow";

    document.getElementById("hero-summary-section").style.display = "none";
    document.getElementById("tabs-container").style.display = "none";
    hideAllTabs();
    document.getElementById("section-comparison").classList.remove("hidden");

    try {
        const resp = await fetch('/api/comparison');
        const ranking = await resp.json();
        
        document.getElementById("comp-winner-title").innerText = `Top Selected Candidate: ${ranking.top_candidate} (+${ranking.score_gap} pts gap)`;
        document.getElementById("comp-rationale").innerText = ranking.recommendation_summary;

        const body = document.getElementById("comp-table-body");
        body.innerHTML = ranking.comparison_matrix.map(row => `
            <tr class="hover:bg-slate-800/40">
                <td class="py-3 px-4 font-bold text-teal-300">${row.dimension}</td>
                <td class="py-3 px-4 text-slate-300">${row.candidate_a}</td>
                <td class="py-3 px-4 text-slate-300">${row.candidate_b}</td>
                <td class="py-3 px-4 font-bold text-indigo-400">${row.winner}</td>
            </tr>
        `).join('');

    } catch (err) {
        console.error("Error fetching comparison:", err);
    }
}

function switchTab(tabId) {
    currentTab = tabId;
    hideAllTabs();
    document.getElementById(tabId).classList.remove("hidden");

    const tabs = ["tab-evals", "tab-debate", "tab-decision", "tab-facts"];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t.replace('tab-', '')}`);
        if (t === tabId) {
            btn.className = "pb-3 border-b-2 border-teal-500 text-teal-400 flex items-center gap-2";
        } else {
            btn.className = "pb-3 border-b-2 border-transparent text-slate-400 hover:text-white flex items-center gap-2";
        }
    });
}

function hideAllTabs() {
    const tabs = document.querySelectorAll(".tab-content");
    tabs.forEach(t => t.classList.add("hidden"));
}

function showCurrentTab() {
    switchTab(currentTab);
}

function selectCandidate(cid) {
    loadCandidateData(cid);
}

// Voice Debate Session Player (Web Speech API)
function playVoiceDebate() {
    if (!currentData || !currentData.debate_data) return;
    stopVoiceDebate();

    if (!('speechSynthesis' in window)) {
        alert("Web Speech API not supported in this browser.");
        return;
    }

    const turns = currentData.debate_data.debate_transcript;
    isVoicePlaying = true;
    let turnIdx = 0;

    function speakNextTurn() {
        if (!isVoicePlaying || turnIdx >= turns.length) {
            stopVoiceDebate();
            return;
        }

        const t = turns[turnIdx];
        
        // Highlight active turn in UI
        turns.forEach((_, i) => {
            const elem = document.getElementById(`debate-turn-${i}`);
            if (elem) elem.style.opacity = (i === turnIdx) ? '1' : '0.5';
        });

        speechUtterance = new SpeechSynthesisUtterance(`${t.speaker} says: ${t.text}`);
        
        // Voice pitch tuning per agent persona
        if (t.speaker.includes("Technical")) {
            speechUtterance.pitch = 0.9;
            speechUtterance.rate = 1.0;
        } else if (t.speaker.includes("HR")) {
            speechUtterance.pitch = 1.25;
            speechUtterance.rate = 1.05;
        } else if (t.speaker.includes("Hiring Manager")) {
            speechUtterance.pitch = 0.85;
            speechUtterance.rate = 1.1;
        } else { // Skeptic
            speechUtterance.pitch = 1.0;
            speechUtterance.rate = 0.95;
        }

        speechUtterance.onend = () => {
            turnIdx++;
            speakNextTurn();
        };

        speechUtterance.onerror = () => {
            turnIdx++;
            speakNextTurn();
        };

        window.speechSynthesis.speak(speechUtterance);
    }

    document.getElementById("btn-play-voice").innerHTML = `<i class="fa-solid fa-volume-high animate-pulse"></i> Playing Debate...`;
    speakNextTurn();
}

function stopVoiceDebate() {
    isVoicePlaying = false;
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    const btn = document.getElementById("btn-play-voice");
    if (btn) {
        btn.innerHTML = `<i class="fa-solid fa-play"></i> Play Voice Debate`;
    }
    if (currentData && currentData.debate_data) {
        currentData.debate_data.debate_transcript.forEach((_, i) => {
            const elem = document.getElementById(`debate-turn-${i}`);
            if (elem) elem.style.opacity = '1';
        });
    }
}
