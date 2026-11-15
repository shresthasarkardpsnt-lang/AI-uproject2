"""Technical Mono Y2K look: monospace type, chrome title bars, hard offset shadows, CRT terminal hero, acid colours.

Plain HTML + CSS only (no external fonts, images or scripts, so it works offline). Every dynamic string goes through
`esc`. The stylesheet forces a light base so the page stays readable when Streamlit or the browser is in dark mode.
"""
from __future__ import annotations

import html

import streamlit as st


class Raw(str):
    """Marks a string as already-safe HTML."""


def esc(x) -> str:
    return x if isinstance(x, Raw) else html.escape("" if x is None else str(x))


CSS = """
<style>
:root{--bg:#D9DEE7;--grid:rgba(20,30,90,.09);--panel:#F4F6FA;--silver:#C6CCD8;--ink:#0A0F1F;--muted:#4A5368;
--blue:#2D3BFF;--cyan:#00D1FF;--mag:#FF2E93;--lime:#B8FF2C;--yel:#FFD60A;--ok:#17D064;--rv:#FFC400;--no:#FF3366;
--crt:#05070D;--crt-t:#7CFF9B;--mono:ui-monospace,"Cascadia Code","SF Mono",Menlo,Consolas,"Liberation Mono","Courier New",monospace;
--chrome:linear-gradient(180deg,#FFFFFF 0%,#DDE2EC 48%,#B9C1D1 52%,#E7EBF3 100%)}
:root,html,body,.stApp{color-scheme:light!important}
.stApp{background-color:var(--bg);background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:22px 22px;color:var(--ink)}
.stApp,.stApp p,.stApp li,.stApp label,.stApp input,.stApp textarea,.stApp button,.stApp summary,.stApp td,.stApp th,.stApp code,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp div[data-baseweb]{font-family:var(--mono)!important}
.block-container{max-width:1140px;padding-top:1.2rem;padding-bottom:5rem}
header[data-testid="stHeader"]{background:var(--chrome)!important;border-bottom:2px solid var(--ink)}
header[data-testid="stHeader"] *,[data-testid="stToolbar"] *{color:var(--ink)!important}
.stApp,.stApp p,.stApp li,.stApp label,.stApp [data-testid="stWidgetLabel"] *,.stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li{color:var(--ink)}
.stApp h1,.stApp h2,.stApp h3{color:var(--ink)!important;text-transform:uppercase;letter-spacing:.04em;font-weight:800}
.stApp h2,.stApp h3{border-bottom:2px solid var(--ink);padding-bottom:4px;display:inline-block;background:linear-gradient(transparent 62%,var(--lime) 62%)}
.stApp [data-testid="stWidgetLabel"] p{font-weight:700;text-transform:uppercase;font-size:.74rem;letter-spacing:.08em;color:var(--blue)!important}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{color:var(--muted)!important;font-size:.78rem}
section[data-testid="stSidebar"]{background:var(--chrome);border-right:2px solid var(--ink)}
section[data-testid="stSidebar"] *{color:var(--ink)}
.aps-brand{font-weight:800;font-size:1.05rem;letter-spacing:.06em;background:var(--ink);color:var(--lime)!important;padding:8px 10px;border:2px solid var(--ink);box-shadow:4px 4px 0 var(--blue);text-transform:uppercase}
.aps-brandsub{font-size:.7rem;color:var(--muted);margin:8px 0 12px;letter-spacing:.05em;text-transform:uppercase}
.aps-hero{border:2px solid var(--ink);box-shadow:8px 8px 0 var(--ink);margin:4px 0 22px;background:var(--crt)}
.aps-tb,.aps-ct{display:flex;justify-content:space-between;align-items:center;padding:6px 10px;font-size:.74rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;border-bottom:2px solid var(--ink)}
.aps-tb{background:linear-gradient(90deg,#1B1FD6,var(--blue) 40%,var(--cyan));color:#fff}.aps-tb span:last-child{letter-spacing:.3em}
.aps-hb{position:relative;padding:22px 26px 24px;background-image:repeating-linear-gradient(0deg,rgba(124,255,155,.06) 0,rgba(124,255,155,.06) 1px,transparent 1px,transparent 3px)}
.aps-hb:after{content:"";position:absolute;right:18px;top:16px;width:92px;height:46px;background:repeating-linear-gradient(90deg,var(--mag) 0 3px,transparent 3px 6px,var(--cyan) 6px 8px,transparent 8px 12px);opacity:.85}
.aps-badge{display:inline-block;border:1px solid var(--crt-t);color:var(--crt-t);font-size:.7rem;letter-spacing:.12em;padding:2px 8px;margin-bottom:10px;text-transform:uppercase}
.aps-hero h1{margin:0 0 8px 0;padding:0;font-size:1.95rem;color:var(--crt-t)!important;text-shadow:0 0 10px rgba(124,255,155,.55);border:none!important;background:none!important;display:block}
.aps-hero p{margin:0;color:#9BE7FF;font-size:.92rem;max-width:760px}.aps-hero p:before{content:"> ";color:var(--mag)}
.cur{display:inline-block;width:.55em;height:1em;background:var(--lime);margin-left:8px;vertical-align:-3px;animation:blink 1s steps(2) infinite}
@keyframes blink{50%{opacity:0}}
.aps-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:16px;margin:8px 0 22px}
.aps-stat{background:var(--panel);border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink);padding:0}
.aps-st{font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:4px 10px;border-bottom:2px solid var(--ink)}
.aps-ok .aps-st{background:var(--ok)}.aps-rv .aps-st{background:var(--rv)}.aps-no .aps-st{background:var(--no);color:#fff}.aps-in .aps-st{background:var(--cyan)}
.aps-sn{font-size:2.3rem;font-weight:800;padding:8px 12px 10px;line-height:1}
.aps-card{background:var(--panel);border:2px solid var(--ink);box-shadow:6px 6px 0 var(--ink);margin:18px 0 6px}
.aps-ct{color:var(--ink)}.aps-card.ok .aps-ct{background:linear-gradient(90deg,var(--ok),var(--lime))}.aps-card.rv .aps-ct{background:linear-gradient(90deg,var(--rv),var(--yel))}.aps-card.no .aps-ct{background:linear-gradient(90deg,var(--no),#FF8FB1)}
.aps-ct b{border:1.5px solid var(--ink);background:#fff;padding:1px 7px;font-size:.68rem}
.aps-body{padding:12px 16px 14px}.aps-body .aps-sub{margin-bottom:8px}
.aps-sub{font-size:.76rem;color:var(--muted);letter-spacing:.03em}
.aps-pill{display:inline-block;border:1.5px solid var(--ink);padding:1px 8px;font-size:.68rem;font-weight:800;margin:2px 6px 2px 0;text-transform:uppercase;letter-spacing:.05em}
.p-ok{background:var(--lime)}.p-no{background:var(--no);color:#fff}.p-rv{background:var(--yel)}.p-in{background:var(--cyan)}.p-mu{background:var(--silver)}
.aps-gauge{display:flex;gap:2px;align-items:center;margin:10px 0 2px}.aps-gauge i{flex:1;height:12px;border:1px solid var(--ink);background:#fff}
.aps-gauge i.on{background:var(--ok)}.aps-gauge.rv i.on{background:var(--rv)}.aps-gauge.no i.on{background:var(--no)}
.aps-gauge em{font-style:normal;font-size:.72rem;font-weight:800;margin-left:8px;white-space:nowrap}
.aps-meter{height:12px;border:1.5px solid var(--ink);background:#fff;display:flex;margin:8px 0 2px}
.aps-meter i{display:block;height:100%}.m-ok{background:var(--ok)}.m-no{background:var(--no)}.m-rv{background:var(--rv)}
.aps-table{width:100%;border-collapse:collapse;font-size:.8rem;margin:10px 0 18px;background:var(--panel);border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink)}
.aps-table th{text-align:left;padding:8px 10px;background:var(--ink);color:var(--lime);font-weight:800;font-size:.7rem;letter-spacing:.09em;text-transform:uppercase}
.aps-table td{padding:8px 10px;border-bottom:1px dashed rgba(10,15,31,.35);vertical-align:top}
.aps-table tr:nth-child(even) td{background:rgba(45,59,255,.05)}.aps-table tr:last-child td{border-bottom:none}
.aps-bar{position:relative;height:12px;border:1.5px solid var(--ink);background:#fff;min-width:120px;margin-top:3px}
.aps-bar i{position:absolute;left:0;top:0;bottom:0}.aps-bar u{position:absolute;top:-6px;bottom:-6px;width:3px;background:var(--mag)}
.aps-chain{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:10px 0}
.aps-chip{border:2px solid var(--ink);background:#fff;padding:4px 10px;font-size:.76rem;font-weight:700;box-shadow:3px 3px 0 var(--ink)}
.aps-chip.start{background:var(--yel)}.aps-chip.goal{background:var(--ink);color:var(--lime)}.aps-arrow{color:var(--mag);font-weight:800}
.aps-step{display:flex;gap:12px;margin:12px 0;padding:10px 14px;background:var(--panel);border:2px solid var(--ink);box-shadow:4px 4px 0 var(--ink)}
.aps-num{flex:0 0 30px;height:30px;background:var(--ink);color:var(--lime);font-weight:800;display:flex;align-items:center;justify-content:center;font-size:.82rem}
.aps-step small{display:block;color:var(--muted);margin-top:3px;font-size:.75rem}.aps-step code{background:#E4E8F2;color:var(--blue);padding:0 5px;border:1px solid var(--silver)}
.aps-note{border:2px dashed var(--ink);background:#FFF8B8;padding:10px 14px;font-size:.82rem;margin:12px 0}.aps-note:before{content:"[!] ";font-weight:800}
.aps-note.info{background:#D3F4FF}.aps-note.info:before{content:"[i] "}
.aps-flow{display:flex;gap:6px;margin:2px 0 10px;flex-wrap:wrap}.aps-flow span{flex:1;min-width:110px;text-align:center;padding:5px;border:2px solid var(--ink);background:#fff;font-size:.74rem}.aps-flow span.on{background:var(--ink);color:var(--lime)}
.aps-src{display:inline-block;border:2px solid var(--ink);padding:1px 8px;font-size:.68rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;background:var(--lime)}.aps-src.ai{background:var(--mag);color:#fff}
div[data-testid="stRadio"] [role="radiogroup"]{gap:8px;flex-wrap:wrap}
div[data-testid="stRadio"] label[data-baseweb="radio"]{background:var(--chrome);border:2px solid var(--ink);padding:5px 12px;margin:0;box-shadow:3px 3px 0 var(--ink);transition:transform .08s}
div[data-testid="stRadio"] label[data-baseweb="radio"]>div:first-child{display:none}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover{transform:translate(-1px,-1px);box-shadow:4px 4px 0 var(--blue)}
div[data-testid="stRadio"] label[data-baseweb="radio"] *{color:var(--ink);font-weight:700;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked){background:var(--ink)}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) *{color:var(--lime)!important;-webkit-text-fill-color:var(--lime)!important}
button[data-baseweb="tab"]{border:2px solid var(--ink);border-bottom:none;background:var(--silver);margin-right:4px;font-weight:800;text-transform:uppercase;font-size:.75rem}
button[data-baseweb="tab"] p{color:var(--ink)!important;font-size:.75rem}button[data-baseweb="tab"][aria-selected="true"]{background:var(--ink)}button[data-baseweb="tab"][aria-selected="true"] p{color:var(--lime)!important}
div[data-baseweb="tab-highlight"],div[data-baseweb="tab-border"]{background:var(--ink)!important;height:2px!important}
div[data-testid="stExpander"]{background:var(--panel);border:2px solid var(--ink)!important;border-radius:0!important;box-shadow:4px 4px 0 var(--ink);margin:6px 0 10px}
div[data-testid="stExpander"] details,div[data-testid="stExpander"] summary{background:var(--panel);border-radius:0!important}
div[data-testid="stExpander"] summary{background:var(--chrome);border-bottom:2px solid var(--ink)}div[data-testid="stExpander"] summary *{color:var(--ink)!important;font-weight:800;text-transform:uppercase;font-size:.78rem;letter-spacing:.04em}
div[data-baseweb="input"],div[data-baseweb="base-input"],div[data-baseweb="select"]>div,div[data-baseweb="textarea"],textarea{background:#fff!important;border:2px solid var(--ink)!important;border-radius:0!important;box-shadow:inset 2px 2px 0 rgba(10,15,31,.12)}
div[data-baseweb="input"]:focus-within,div[data-baseweb="select"]>div:focus-within{border-color:var(--blue)!important;box-shadow:3px 3px 0 var(--blue)!important}
input,textarea,div[data-baseweb="select"] *{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;background-color:transparent}
input::placeholder,textarea::placeholder{color:#7C869A!important;-webkit-text-fill-color:#7C869A!important}
div[data-baseweb="select"] svg,div[data-baseweb="input"] svg{fill:var(--ink)!important}
div[data-testid="stNumberInput"] button{background:var(--silver)!important;color:var(--ink)!important;border-radius:0!important}
div[data-baseweb="popover"],div[data-baseweb="popover"] ul,div[data-baseweb="menu"],ul[role="listbox"]{background:#fff!important;border:2px solid var(--ink);border-radius:0!important}
div[data-baseweb="popover"] li,ul[role="listbox"] li,ul[role="listbox"] li *{background:#fff!important;color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important}
ul[role="listbox"] li:hover,ul[role="listbox"] li[aria-selected="true"]{background:var(--lime)!important}
div[data-testid="stForm"]{background:var(--panel);border:2px solid var(--ink)!important;border-radius:0!important;box-shadow:6px 6px 0 var(--ink);padding:8px 12px}
.stButton>button,.stDownloadButton>button,div[data-testid="stFormSubmitButton"]>button{background:var(--chrome)!important;color:var(--ink)!important;-webkit-text-fill-color:var(--ink);border:2px solid var(--ink)!important;border-radius:0!important;box-shadow:4px 4px 0 var(--ink);font-weight:800;text-transform:uppercase;letter-spacing:.05em;font-size:.78rem;transition:transform .08s}
.stButton>button p,.stDownloadButton>button p,div[data-testid="stFormSubmitButton"]>button p{color:inherit!important;font-size:.78rem}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translate(-1px,-1px);box-shadow:6px 6px 0 var(--blue)}
.stButton>button:active{transform:translate(3px,3px);box-shadow:1px 1px 0 var(--ink)}
.stButton>button[kind="primary"],div[data-testid="stFormSubmitButton"]>button[kind="primary"]{background:linear-gradient(180deg,#EAFF9A,var(--lime))!important}
div[data-testid="stAlert"]{border:2px solid var(--ink);border-radius:0;box-shadow:4px 4px 0 var(--ink)}div[data-testid="stAlert"],div[data-testid="stAlert"] *{color:var(--ink)!important}
div[data-testid="stCheckbox"] label *,div[data-testid="stSlider"] *{color:var(--ink)}
div[data-testid="stSlider"] [data-testid="stThumbValue"]{color:var(--blue)!important;font-weight:800}
div[data-testid="stChatMessage"]{background:var(--panel);border:2px solid var(--ink);border-radius:0;box-shadow:4px 4px 0 var(--ink);margin-bottom:12px}
div[data-testid="stChatMessage"] *{color:var(--ink)}
div[data-testid="stChatInput"],div[data-testid="stChatInput"]>div{background:#fff!important;border:2px solid var(--ink)!important;border-radius:0!important}
div[data-testid="stBottom"],div[data-testid="stBottom"]>div{background:var(--bg)!important}
pre,div[data-testid="stCode"]{border:2px solid var(--ink)!important;border-radius:0!important;box-shadow:4px 4px 0 var(--ink)}
hr{border:none!important;border-top:2px dashed var(--ink)!important;opacity:.5}
.stApp .aps-hero h1{color:var(--crt-t)!important}.stApp .aps-hero p{color:#9BE7FF!important}.stApp .aps-badge{color:var(--crt-t)!important}
.stApp .aps-tb,.stApp .aps-tb span{color:#fff!important}.stApp .aps-table th{color:var(--lime)!important}.stApp .aps-num{color:var(--lime)!important}
.stApp .aps-chip.goal{color:var(--lime)!important}.stApp .aps-no .aps-st,.stApp .aps-pill.p-no{color:#fff!important}.stApp .aps-src.ai{color:#fff!important}
.stApp .aps-brand{color:var(--lime)!important}.stApp .aps-flow span.on{color:var(--lime)!important}
.stApp .aps-note,.stApp .aps-note *{color:var(--ink)!important}
</style>
"""

DECISION = {"Eligible": ("ok", "[ OK ] ELIGIBLE"), "Not eligible": ("no", "[ X ] NOT ELIGIBLE"), "Needs review": ("rv", "[ ? ] NEEDS REVIEW")}
CONF = {"High": "ok", "Medium": "rv", "Low": "no"}
REVIEW = {"auto": "p-ok", "check": "p-rv", "input": "p-in", "human": "p-no"}
TRI = {"TRUE": ("ok", "MET"), "FALSE": ("no", "NOT MET"), "UNKNOWN": ("rv", "UNKNOWN")}


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def show(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def hero(title: str, subtitle: str, badge: str = "SYS.ONLINE // PATHWAY.EXE") -> None:
    show(f"<div class='aps-hero'><div class='aps-tb'><span>■ pathway_finder.exe</span><span>_▢✕</span></div>"
         f"<div class='aps-hb'><span class='aps-badge'>{esc(badge)}</span><h1>{esc(title)}<i class='cur'></i></h1><p>{esc(subtitle)}</p></div></div>")


def flow(labels: list, active: str) -> None:
    show("<div class='aps-flow'>" + "".join(f"<span class='{'on' if l == active else ''}'>{esc(l)}</span>" for l in labels) + "</div>")


def pill(text, kind: str = "mu") -> Raw:
    return Raw(f"<span class='aps-pill p-{kind}'>{esc(text)}</span>")


def pill_raw(text, css: str) -> Raw:
    return Raw(f"<span class='aps-pill {css}'>{esc(text)}</span>")


def source_tag(source: str) -> Raw:
    return Raw(f"<span class='aps-src {'ai' if source == 'claude' else ''}'>{'AI: CLAUDE (online)' if source == 'claude' else 'AI: OFFLINE RULES'}</span>")


def stats(items: list) -> None:
    """items: (number, label, css) triples."""
    fmt = lambda n: f"{n:02d}" if isinstance(n, int) else esc(n)
    show("<div class='aps-stats'>" + "".join(f"<div class='aps-stat {c}'><div class='aps-st'>// {esc(l)}</div><div class='aps-sn'>{fmt(n)}</div></div>" for n, l, c in items) + "</div>")


def window(kind: str, title: str, tag: str, body: str) -> str:
    return (f"<div class='aps-card {kind}'><div class='aps-ct'><span>▣ {esc(title)}</span><b>{esc(tag)}</b></div>"
            f"<div class='aps-body'>{body}</div></div>")


def gauge(pct: float, kind: str) -> Raw:
    """Segmented progress gauge (20 blocks): share of conditions met."""
    on = round(max(0, min(pct, 100)) / 5)
    return Raw(f"<div class='aps-gauge {kind}'>" + "".join(f"<i class='{'on' if i < on else ''}'></i>" for i in range(20)) + f"<em>{pct:.0f}% MET</em></div>")


def meter(passed: int, failed: int, unknown: int) -> Raw:
    t = max(passed + failed + unknown, 1)
    seg = lambda n, c: f"<i class='{c}' style='width:{100 * n / t:.1f}%'></i>" if n else ""
    return Raw(f"<div class='aps-meter'>{seg(passed, 'm-ok')}{seg(unknown, 'm-rv')}{seg(failed, 'm-no')}</div>")


def bar(value, required, state: str) -> Raw:
    """Marks bar: fill = your mark, magenta tick = required mark. Non-numeric values give an empty cell."""
    try:
        v, r = float(str(value).rstrip("%")), float(str(required).rstrip("%"))
    except ValueError:
        return Raw("")
    colour = {"TRUE": "#17D064", "FALSE": "#FF3366"}.get(state, "#FFC400")
    return Raw(f"<div class='aps-bar'><i style='width:{max(0, min(v, 100)):.1f}%;background:{colour}'></i><u style='left:{max(0, min(r, 100)):.1f}%'></u></div>")


def table(headers: list, rows: list) -> None:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in rows)
    show(f"<table class='aps-table'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")


def chain(chips: list) -> Raw:
    """chips: (text, css) pairs joined by arrows."""
    parts = []
    for i, (text, css) in enumerate(chips):
        parts.append(f"<span class='aps-chip {css}'>{esc(text)}</span>")
        if i < len(chips) - 1:
            parts.append("<span class='aps-arrow'>&gt;&gt;</span>")
    return Raw("<div class='aps-chain'>" + "".join(parts) + "</div>")


def note(text: str, info: bool = False) -> None:
    show(f"<div class='aps-note{' info' if info else ''}'>{esc(text)}</div>")
