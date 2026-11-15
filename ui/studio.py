"""Applicant interface: six short pages in the Technical Mono Y2K style, plain-HTML visuals, an AI assistant that explains.

  01 PROFILE ........ enter marks (blank = unknown)        04 REASONING ..... chain, evidence, exceptions, baseline
  02 PROGRAMMES ..... eligibility, confidence, review     05 AI ASSISTANT .. ask questions; engine decides, AI explains
  03 GAPS+ROUTES .... missing conditions, alt. pathways    06 QUALITY ....... KB, test cases, measured metrics
"""
from __future__ import annotations

import os

import streamlit as st

from engine import applicant as A
from engine import assistant as AI
from engine.constants import LEVELS
from engine.evaluation import run_suite
from engine.reports import evaluation_pdf
from engine.simulator import simulate
from . import common, lite_profile, theme
from .theme import Raw, esc

PAGES = ["01 PROFILE", "02 PROGRAMMES", "03 GAPS+ROUTES", "04 REASONING", "05 AI ASSISTANT", "06 QUALITY"]
ASSISTANT = PAGES[4]


# ------------------------------------------------------------------ shared bits
def need_profile() -> dict:
    p = common.current_profile()
    if p is None:
        theme.note("No student loaded. Choose one in the sidebar, or open 01 PROFILE and load the demo student.")
        st.stop()
    return p


def card_html(c: dict) -> str:
    kind, label = theme.DECISION[c["decision"]]
    conf, rv = c["confidence"], c["review"]
    pct = 100 * c["passed"] / max(c["total"], 1)
    body = (f"<div class='aps-sub'>{esc(c['level'])} // {esc(c['field'])}</div>"
            f"{theme.pill('CONF: ' + conf['label'], theme.CONF[conf['label']])}{theme.pill_raw(rv['label'], theme.REVIEW[rv['code']])}"
            f"<div style='margin:8px 0 2px'>{esc(c['headline'])}</div>{theme.gauge(pct, kind)}"
            f"<div class='aps-sub'>{c['passed']} met / {c['unknown']} unknown / {c['failed']} not met (of {c['total']} conditions)</div>")
    return theme.window(kind, c["name"], label, body)


def chain_html(steps: list) -> str:
    out = []
    for s in steps:
        kind, lab = theme.TRI[s["result"]]
        kids = "".join(f"<small>&nbsp;&nbsp;+ {esc(k['label'])}: {esc(k['student_input'])} -> {esc(theme.TRI[k['result']][1])}</small>" for k in s["children"])
        out.append(f"<div class='aps-step'><div class='aps-num'>{s['n']:02d}</div><div><b>{esc(s['label'])}</b> {theme.pill(lab, kind)}"
                   f"<small>YOU: {esc(s['student_input'])} // NEEDED: {esc(s['requirement'])}</small>"
                   f"<small>RULE: <code>{esc(s['logical_rule'])}</code></small>"
                   f"<small>EVIDENCE: {esc(s['evidence'])}</small><small>{esc(s['explanation'])}</small>{kids}</div></div>")
    return "".join(out)


def conclusion_block(c: dict) -> None:
    conf, rv = c["confidence"], c["review"]
    theme.show("<div class='aps-note info'>"
               f"<b>CONCLUSION:</b> {esc(A.conclusion_sentence(c['result']))}<br>"
               f"<b>CONFIDENCE {esc(conf['label'].upper())}</b> ({conf['pct']:.0%} checked): {esc(conf['basis'])}<br>"
               f"<b>{esc(rv['label'].upper())}:</b> {esc(rv['why'])}</div>")


def exceptions_block(c: dict) -> None:
    theme.table(["Exception", "How it was handled"], [(k, m) for k, m in c["exceptions"]])


def pick(cards: list, key: str, label: str, profile: dict, prefer_open: bool = True) -> dict:
    by = {c["id"]: c for c in cards}
    pref = profile.get("preferred_programme")
    default = pref if pref in by else next((c["id"] for c in cards if prefer_open and c["decision"] != "Eligible"), cards[0]["id"])
    if st.session_state.get(key) not in by:
        st.session_state[key] = default
    pid = st.selectbox(label, list(by), key=key, format_func=lambda i: f"{by[i]['name']}  //  {by[i]['decision']}")
    return by[pid]


def ask_ai(question: str) -> None:
    """Button callback: queue a question and jump to the assistant page."""
    st.session_state["ai_pending"] = question
    st.session_state["nav_page"] = ASSISTANT


# ------------------------------------------------------------------ 01 profile
def page_profile() -> None:
    theme.hero("TELL US ABOUT YOURSELF", "Fill in what you know. Blank means unknown. Nothing is guessed.", "INPUT.MODULE // STEP 01")
    lite_profile.render()


# ------------------------------------------------------------------ 02 programmes
def page_programmes() -> None:
    profile, kb = need_profile(), common.get_kb()
    cards = A.programme_cards(profile, kb)
    sid = profile["student_id"]
    n = lambda d: sum(1 for c in cards if c["decision"] == d)
    queue = [c for c in cards if c["review"]["code"] != "auto" and not st.session_state.get(f"rv_{sid}_{c['id']}")]
    theme.hero("YOUR PROGRAMMES", f"{profile.get('name') or sid}: every programme checked against its rules, with reasons.", "RESULTS.MODULE // STEP 02")
    theme.stats([(n("Eligible"), "Eligible", "aps-ok"), (n("Needs review"), "Needs review", "aps-rv"),
                 (n("Not eligible"), "Not eligible", "aps-no"), (len(queue), "Awaiting human", "aps-in")])
    a, b, c3 = st.columns([2, 3, 2])
    q = a.text_input("Search", key="pg_q", placeholder="data, B.Tech, MCA...").strip().lower()
    show_ = b.radio("Show", ["All", "Eligible", "Needs review", "Not eligible"], horizontal=True, key="pg_show")
    level = c3.selectbox("Level", ["All"] + LEVELS, key="pg_level")
    rows = [c for c in cards if (show_ == "All" or c["decision"] == show_) and (level == "All" or c["level"] == level)
            and (not q or q in c["name"].lower() or q in c["field"].lower())]
    if not rows:
        theme.note("No programme matches these filters.")
    for c in rows:
        theme.show(card_html(c))
        with st.expander("WHY? REASONING / EVIDENCE / EXCEPTIONS"):
            conclusion_block(c)
            st.markdown("**REASONING CHAIN**")
            theme.show(chain_html(A.reasoning_chain(c["result"])))
            st.markdown("**EXCEPTION HANDLING**")
            exceptions_block(c)
            k1, k2 = st.columns([3, 2])
            if c["review"]["code"] != "auto":
                k1.checkbox("I dealt with this (checked marks / confirmed with institution)", key=f"rv_{sid}_{c['id']}")
            k2.button("ASK THE AI ABOUT THIS", key=f"ai_{sid}_{c['id']}", on_click=ask_ai,
                      args=(f"Why is my result for {c['name']} {c['decision']}, and what should I do?",))
    try:
        st.download_button("DOWNLOAD PDF REPORT", evaluation_pdf(profile, [c["result"] for c in rows or cards]), "eligibility_report.pdf", "application/pdf")
    except Exception:  # the report is optional; never block the page
        st.caption("PDF report unavailable right now.")
    st.caption("Sample criteria are illustrative, not official. Confirm with the institution.")


# ------------------------------------------------------------------ 03 gaps + pathways
def page_gaps() -> None:
    profile, kb = need_profile(), common.get_kb()
    cards = A.programme_cards(profile, kb)
    theme.hero("WHAT'S MISSING + OTHER ROUTES", "Pick a programme: see the exact gaps and the alternative pathways.", "GAP.MODULE // STEP 03")
    c = pick(cards, "studio_gap_prog", "Programme", profile)
    r, a = c["result"], c["analysis"]
    theme.show(card_html(c))
    rows = []
    for k in r.conditions:
        kind, lab = theme.TRI[k.result.value]
        status = lab if k.result.value != "FALSE" else "NOT MET: " + k.gap_text.replace(" percentage points", " pts short")
        rows.append((k.label, k.student_value, k.required, theme.bar(k.student_value, k.required, k.result.value), theme.pill(status, kind)))
    theme.table(["Requirement", "You", "Needed", "Your mark vs needed (pink tick)", "Status"], rows)
    left, right = st.columns(2)
    with left:
        if a["information_required"]:
            st.markdown("**ADD TO YOUR PROFILE**")
            for m in dict.fromkeys(a["information_required"]):
                st.markdown(f"- {m}")
    with right:
        if a["next_steps"]:
            st.markdown("**WHAT YOU CAN DO**")
            for s in dict.fromkeys(a["next_steps"]):
                st.markdown(f"- {s}")
    if c["decision"] == "Eligible":
        st.success("Nothing is missing for this programme.")
    st.button("ASK THE AI WHAT TO DO NEXT", key="ai_gap", on_click=ask_ai, args=(f"What is the quickest way into {c['name']}?",))
    st.divider()
    st.subheader("Alternative pathways")
    routes = A.pathways(profile, c["id"], kb)
    if not routes:
        theme.note("No alternative route to this programme is defined in the sample knowledge base.")
    for i, p in enumerate(routes):
        with st.expander(f"{'[GO] CAN START NOW' if p['feasible_now'] else '[WAIT] NOT YET'}  //  {p['name']}", expanded=(i == 0)):
            chips = [("YOU ARE HERE", "start")] + [(lab, "goal" if j == len(p["chain"]) - 1 else "") for j, (_, lab, _) in enumerate(p["chain"])]
            theme.show(str(theme.chain(chips)))
            st.markdown(f"*{p['type']}.* {p['why']}")
            st.markdown(f"**ENTRY CHECK:** {p['why_now']}")
            if p["blocking"]:
                st.markdown("**PREREQUISITES STILL BLOCKING STEP 1**")
                for lab, gap in p["blocking"]:
                    st.markdown(f"- {lab}: {gap}")
            st.markdown("**STEPS TO COMPLETE**")
            for s in p["to_do"]:
                st.markdown(f"- {s}")
            st.caption(f"{p['recognition']} Source status: {p['verification']}. {p['disclaimer']}")
    ov = A.pathway_overview(profile, kb)
    if ov:
        with st.expander("ALL NOT-ELIGIBLE PROGRAMMES: IS THERE A ROUTE YOU CAN START TODAY?"):
            theme.table(["Programme", "Result", "Routes known", "Startable now"],
                        [(o["name"], o["decision"], o["routes"], ", ".join(o["ready"]) or "None") for o in ov])
    st.divider()
    what_if(profile, kb)


def what_if(profile: dict, kb: dict) -> None:
    st.subheader("What-if simulator")
    st.caption("Hypothetical only. Your saved profile never changes. Only sliders you move are simulated.")
    sid = profile["student_id"]
    spec = [("Overall %", "overall_pct", profile.get("overall_pct")), ("Mathematics %", "mathematics", profile["marks"].get("mathematics")),
            ("Physics %", "physics", profile["marks"].get("physics")), ("Chemistry %", "chemistry", profile["marks"].get("chemistry"))]
    cols, over, marks = st.columns(4), {}, {}
    for col, (label, key, cur) in zip(cols, spec):
        start = int(cur) if cur is not None else 50
        v = col.slider(label, 0, 100, start, key=f"wi_{sid}_{key}")
        if v != start:
            (over if key == "overall_pct" else marks)[key] = v
    if not over and not marks:
        st.info("Move a slider to see which programmes would change.")
        return
    sim = simulate(profile, {**over, "marks": marks}, kb)
    a, b = st.columns(2)
    a.success("NEWLY ELIGIBLE: " + (", ".join(sim["newly_eligible"]) or "none"))
    b.warning("NO LONGER ELIGIBLE: " + (", ".join(sim["no_longer_eligible"]) or "none"))
    changed = [(x["Programme"], x["Current"], x["Hypothetical"]) for x in sim["rows"] if x["Changed"] == "Yes"]
    if changed:
        theme.table(["Programme", "Now", "If marks changed"], changed)
    if sim["remaining_failed"]:
        with st.expander("STILL NOT MET EVEN WITH THESE MARKS"):
            for name, items in sim["remaining_failed"].items():
                st.markdown(f"**{name}**: " + "; ".join(f"{l} ({g})" for l, g in items))


# ------------------------------------------------------------------ 04 reasoning
def page_reasoning() -> None:
    profile, kb = need_profile(), common.get_kb()
    cards = A.programme_cards(profile, kb)
    theme.hero("HOW EACH ANSWER WAS REACHED", "Rule, your input, evidence and result for every condition. No black box.", "TRACE.MODULE // STEP 04")
    c = pick(cards, "studio_reason_prog", "Programme", profile, prefer_open=False)
    r = c["result"]
    theme.show(card_html(c))
    conclusion_block(c)
    t1, t2, t3, t4 = st.tabs(["REASONING CHAIN", "EVIDENCE + RULE", "EXCEPTIONS", "VS SIMPLE IF/ELSE"])
    with t1:
        theme.show(chain_html(A.reasoning_chain(r)))
    with t2:
        src = r.source or {}
        st.markdown("**RULE USED**")
        st.code(r.rule_expression, language=None)
        theme.table(["Item", "Value"], [("Rule version", f"v{r.rule_version}"), ("Source", src.get("name", "unknown")),
                                        ("Verification", src.get("verification_status", "Unverified")),
                                        ("Verified on", src.get("verified_on") or "Not verified")])
        st.markdown("**EVIDENCE PER CONDITION**")
        theme.table(["Condition", "Evidence"], [(k.label, k.evidence) for k in r.conditions])
    with t3:
        exceptions_block(c)
    with t4:
        cmp_ = A.baseline_comparison(profile, kb)
        diff = [x for x in cmp_ if not x["agree"]]
        st.markdown(f"On your profile the simple if/else baseline differs from the rule engine on **{len(diff)} of {len(cmp_)}** programmes.")
        theme.table(["Programme", "Rule engine", "Simple if/else", "What differs"],
                    [(x["name"], x["engine"], x["baseline"], x["note"]) for x in sorted(cmp_, key=lambda x: x["agree"])])
        st.caption("The baseline checks only overall %, subject minimums and stream, and treats blanks as zero.")


# ------------------------------------------------------------------ 05 AI assistant
def ai_settings() -> tuple:
    """(mode, api_key, model) from the sidebar widgets; Claude mode needs a key (field or ANTHROPIC_API_KEY)."""
    choice = st.session_state.get("ai_mode_choice", "Offline (rules only)")
    key = (st.session_state.get("ai_key") or os.environ.get("ANTHROPIC_API_KEY", "")).strip()
    mode = "claude" if choice.startswith("Claude") and key else "offline"
    return mode, key, (st.session_state.get("ai_model") or AI.DEFAULT_MODEL).strip()


def page_assistant() -> None:
    profile, kb = need_profile(), common.get_kb()
    sid = profile["student_id"]
    mode, key, model = ai_settings()
    theme.hero("AI ASSISTANT", "Ask in plain English. The rule engine decides. The assistant only explains.", "AI.CORE // GROUNDED IN ENGINE OUTPUT")
    theme.show(f"{theme.source_tag('claude' if mode == 'claude' else 'offline')} &nbsp;"
               f"<span class='aps-sub'>{'Facts are sent to the Anthropic API (your name is not).' if mode == 'claude' else 'Runs fully offline. No data leaves this computer.'}</span>")
    if st.session_state.get("ai_mode_choice", "").startswith("Claude") and not key:
        theme.note("Claude mode is selected but no API key is set. Using the offline assistant. Add a key in the sidebar.")
    hist = st.session_state.setdefault("ai_hist", {}).setdefault(sid, [])
    st.markdown("**QUICK QUESTIONS**")
    q = None
    sugg = AI.suggestions(profile, kb)
    cols = st.columns(2)
    for i, s in enumerate(sugg):
        if cols[i % 2].button(s, key=f"sg_{sid}_{i}"):
            q = s
    queued = st.session_state.pop("ai_pending", None)
    q = st.chat_input("Ask about your results, gaps or routes...") or q or queued
    if q:
        hist.append({"role": "user", "content": q})
        out = AI.answer(q, hist[:-1], profile, kb, mode, key, model)
        verdicts = [(p["name"], p["decision"], p["confidence"]) for p in AI.mentioned(out["text"], out["ctx"])] if out["source"] == "claude" else []
        hist.append({"role": "assistant", "content": out["text"], "source": out["source"], "notice": out["notice"], "verdicts": verdicts})
    if not hist:
        theme.note("No messages yet. Tap a quick question or type your own below.", info=True)
    for m in hist:
        with st.chat_message(m["role"]):
            if m["role"] == "assistant":
                theme.show(str(theme.source_tag(m.get("source", "offline"))))
                if m.get("notice"):
                    st.caption(m["notice"])
            st.markdown(m["content"])
            if m.get("verdicts"):
                st.caption("ENGINE VERDICT (authoritative, from the rules):")
                theme.table(["Programme", "Decision", "Confidence"], m["verdicts"])
    if hist and st.button("CLEAR CHAT", key=f"clr_{sid}"):
        hist.clear()
        st.rerun()
    st.caption("The AI never changes a decision. It cannot see quotas, fees or deadlines. Confirm with the institution.")


# ------------------------------------------------------------------ 06 quality + KB
def page_quality() -> None:
    kb = common.get_kb()
    theme.hero("IS THE SYSTEM RIGHT?", "Knowledge base, documented test cases, measured results vs a simple baseline.", "QA.MODULE // STEP 06")
    s = A.kb_summary(kb)
    theme.stats([(s["programmes"], "Programmes", "aps-in"), (s["rules"], "Rules encoded", "aps-in"), (s["routes"], "Alt. routes", "aps-in"),
                 (s["certificates"], "Certificates", "aps-in")])
    t1, t2, t3 = st.tabs(["KNOWLEDGE BASE", "TEST CASES", "MEASURED RESULTS"])
    with t1:
        st.markdown("**DOCUMENTED ASSUMPTIONS**")
        for a_ in A.ASSUMPTIONS:
            st.markdown(f"- {a_}")
        st.markdown("**COVERAGE:** " + ", ".join(f"{v} {k}" for k, v in s["levels"].items()) + " // rule status: "
                    + ", ".join(f"{v} {k}" for k, v in s["verification"].items()))
        theme.table(["Programme", "Level", "Field", "Rule"],
                    [(p["name"], p["level"], p["field"], " AND ".join(k.rule for k in A.evaluate_programme(A.normalise_profile({}), p).conditions)) for p in kb["programmes"]])
    with t2:
        rows = A.run_cases(kb)
        ok = sum(1 for x in rows if x["pass"])
        st.markdown(f"**{ok} OF {len(rows)} ACCEPTANCE CRITERIA MET.** Each case states its assumption and the decision it must produce.")
        theme.table(["Type", "Case", "Assumption", "Must give", "Got", "Result"],
                    [(x["kind"], x["name"], x["assumption"], x["expected"], x["actual"], "PASS" if x["pass"] else "FAIL") for x in rows])
    with t3:
        a, b, c = st.columns(3)
        n = a.number_input("Synthetic profiles", 50, 2000, 300, 50)
        seed = b.number_input("Random seed", 0, 10 ** 6, 42)
        pm = c.slider("Share of fields blanked", 0.05, 0.6, 0.25, 0.05)
        if st.button("RUN MEASURED EVALUATION", type="primary"):
            with st.spinner("Evaluating..."):
                st.session_state["studio_suite"] = run_suite(kb, int(n), int(seed), float(pm))
        suite = st.session_state.get("studio_suite")
        if not suite:
            st.info("Press the button to measure the rule engine against the simple baseline.")
            return
        quality_results(suite)


def quality_results(sx: dict) -> None:
    e, b, inc, cfg = sx["engine"], sx["baseline"], sx["incomplete"], sx["config"]
    st.caption(f"{cfg['n_profiles']} synthetic profiles x {cfg['programmes']} programmes = {cfg['pairs_complete']} decisions (seed {cfg['seed']}). Not real students.")
    f = lambda m: f"{m:.3f}"
    theme.table(["System", "Accuracy", "Precision", "Recall", "F1", "TP / FP / FN / TN"],
                [("Rule engine", f(e["accuracy"]), f(e["precision"]), f(e["recall"]), f(e["f1"]), f"{e['tp']} / {e['fp']} / {e['fn']} / {e['tn']}"),
                 ("Simple if/else", f(b["accuracy"]), f(b["precision"]), f(b["recall"]), f(b["f1"]), f"{b['tp']} / {b['fp']} / {b['fn']} / {b['tn']}")])
    st.markdown("**WHEN INFORMATION IS MISSING**")
    theme.table(["Measure", "Rule engine", "Simple if/else"],
                [("Gave a definite answer", f"{inc['engine_decision_rate']:.1%}", "100% (always guesses)"),
                 ("Correct when definite", f"{inc['engine_definite_accuracy']:.1%}", f"{inc['baseline_accuracy_vs_truth']:.1%}"),
                 ("False 'Eligible' answers", inc["engine_false_eligible"], inc["baseline_false_eligible"]),
                 ("Sent to Needs review", inc["engine_needs_review"], 0)])
    st.markdown("**FAILURE PATTERNS**")
    st.markdown(f"- The baseline gave **{b['fp']}** false 'Eligible' answers on complete profiles. It ignores entrance exams, qualifications and OR-rules.\n"
                f"- With blanks it gave **{inc['baseline_false_eligible']}** false 'Eligible' answers; the engine gave **{inc['engine_false_eligible']}**.\n"
                f"- The engine never answers wrongly when it answers, but it holds back **{1 - inc['engine_decision_rate']:.1%}** of incomplete cases for review.")
    st.markdown("**TRADE-OFFS**")
    st.markdown("- Caution vs speed: Needs review is slower than a guess but never wrongly tells someone they qualify.\n"
                "- Transparency vs flexibility: every rule is hand-written and explainable, so new rules cost maintenance effort.\n"
                "- A 1.000 score only shows the engine follows the sample rules faithfully (the reference uses the same rules). It does not prove real-world correctness.")
    rc, ec, tm = sx["rule_coverage"], sx["explanation_completeness"], sx["timing_ms"]
    st.caption(f"Rule coverage {rc['rules_exercised']}/{rc['rules_total']} (both outcomes seen: {rc['rules_with_true_and_false']}) // explanation completeness "
               f"{ec['mean']:.0%} // about {tm['mean_per_programme']:.2f} ms per programme (machine-dependent).")
