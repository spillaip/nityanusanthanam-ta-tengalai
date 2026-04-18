import base64
import html
import re
import urllib.parse
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import streamlit as st
from gtts import gTTS

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "assets"
PASURAMS = BASE_DIR / "pasurams"

ICON = ASSETS / "icon.png"

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="நித்யானுசந்தானம்",
    page_icon=str(ICON) if ICON.exists() else "📿",
    layout="wide",
)

# ----------------------------
# Section list
# ----------------------------
SECTION_OPTIONS = [
    "பொதுத் தனியங்கள்",
    "திருப்பல்லாண்டு",
    "திருப்பள்ளியெழுச்சி",
    "திருப்பாவை",
    "நீராட்டம்",
    "பூச்சூடல்",
    "காப்பிடல்",
    "சென்னியோங்கு",
    "அமலனாதிபிரான்",
    "கண்ணிநுண் சிறுதாம்பு",
    "கோயில் திருவாய்மொழி",
    "இராமானுஜ நூற்றந்தாதி",
    "வாரணமாயிரம்",
    "நாலாயிரத் தனியன்கள்",
    "இயல்சாத்து",
    "சாற்றுமுறை",
]

FILE_MAP = {
    "பொதுத் தனியங்கள்": "podhu_thaniyangal.txt",
    "திருப்பல்லாண்டு": "thiruppallandu.txt",
    "திருப்பள்ளியெழுச்சி": "thiruppalliyezhuchchi.txt",
    "திருப்பாவை": "thiruppavai.txt",
    "நீராட்டம்": "neerattam.txt",
    "பூச்சூடல்": "poochoodal.txt",
    "காப்பிடல்": "kaapidal.txt",
    "சென்னியோங்கு": "senniyongu.txt",
    "அமலனாதிபிரான்": "amalanadhi_piran.txt",
    "கண்ணிநுண் சிறுதாம்பு": "kanninunsiruthambu.txt",
    "கோயில் திருவாய்மொழி": "koil_thiruvaimozhi.txt",
    "இராமானுஜ நூற்றந்தாதி": "ramanuja_nootrandhadhi.txt",
    "வாரணமாயிரம்": "varanamayiram.txt",
    "நாலாயிரத் தனியன்கள்": "nalayira_thaniyangal.txt",
    "இயல்சாத்து": "iyal_saatru.txt",
    "சாற்றுமுறை": "saatrumurai.txt",
}

# ----------------------------
# Models
# ----------------------------
@dataclass
class HymnBlock:
    kind: str  # "taniyan" or "pasuram"
    heading: str = ""
    heading2: str = ""
    body: str = ""
    original_no: int = 0


@dataclass
class SectionData:
    title: str
    taniyans: list[HymnBlock]
    pasurams: list[HymnBlock]


# ----------------------------
# State
# ----------------------------
params = st.query_params

if "section" in params and params["section"] in SECTION_OPTIONS:
    st.session_state.selected_section = params["section"]
elif "selected_section" not in st.session_state:
    st.session_state.selected_section = SECTION_OPTIONS[0]

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

target_pasuram_no = None
if "pasuram" in params:
    try:
        target_pasuram_no = int(params["pasuram"])
    except Exception:
        target_pasuram_no = None

# ----------------------------
# Helpers
# ----------------------------
@st.cache_data(show_spinner=False)
def load_text(section_name: str) -> str:
    file_name = FILE_MAP.get(section_name)
    if not file_name:
        return "உள்ளடக்கம் கிடைக்கவில்லை."

    path = PASURAMS / file_name
    if not path.exists():
        return f"கோப்பு கிடைக்கவில்லை: {file_name}"

    return path.read_text(encoding="utf-8")


def file_to_base64(path: Path) -> str:
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def parse_block(kind: str, lines: list[str], original_no: int) -> HymnBlock:
    heading = ""
    heading2 = ""
    body_lines: list[str] = []

    for line in lines:
        s = line.strip()

        if not s:
            body_lines.append("")
            continue

        if s.startswith("<heading>") and s.endswith("</heading>"):
            heading = s[len("<heading>") : -len("</heading>")].strip()
            continue

        if s.startswith("<heading2>") and s.endswith("</heading2>"):
            heading2 = s[len("<heading2>") : -len("</heading2>")].strip()
            continue

        body_lines.append(line.rstrip())

    return HymnBlock(
        kind=kind,
        heading=heading,
        heading2=heading2,
        body="\n".join(body_lines).strip(),
        original_no=original_no,
    )


def parse_section(text: str) -> SectionData:
    title = ""
    current_kind: str | None = None
    current_lines: list[str] = []

    taniyans: list[HymnBlock] = []
    pasurams: list[HymnBlock] = []

    def flush_current() -> None:
        nonlocal current_lines
        if current_kind and current_lines:
            if current_kind == "taniyan":
                block = parse_block("taniyan", current_lines, len(taniyans) + 1)
                if block.heading or block.heading2 or block.body:
                    taniyans.append(block)
            elif current_kind == "pasuram":
                block = parse_block("pasuram", current_lines, len(pasurams) + 1)
                if block.heading or block.heading2 or block.body:
                    pasurams.append(block)
        current_lines = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()

        if not stripped:
            if current_kind is not None:
                current_lines.append("")
            continue

        if stripped.startswith("<title>") and stripped.endswith("</title>"):
            title = stripped[len("<title>") : -len("</title>")].strip()
            continue

        if stripped == "[taniyan]":
            flush_current()
            current_kind = "taniyan"
            continue

        if stripped in ("[pasuram]", "[pasurams]"):
            flush_current()
            current_kind = "pasuram"
            continue

        if stripped == "---":
            flush_current()
            continue

        if current_kind is None:
            continue

        current_lines.append(raw_line.rstrip())

    flush_current()
    return SectionData(title=title, taniyans=taniyans, pasurams=pasurams)


def render_lines(text: str) -> str:
    parts: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            parts.append('<div class="section-gap"></div>')
        else:
            parts.append(f'<div class="verse">{html.escape(s)}</div>')
    return "\n".join(parts)


def render_block(block: HymnBlock) -> str:
    parts: list[str] = []

    if block.heading:
        parts.append(f'<div class="heading">{html.escape(block.heading)}</div>')

    if block.heading2:
        parts.append(f'<div class="heading2">{html.escape(block.heading2)}</div>')

    if block.body:
        parts.append(render_lines(block.body))

    return "".join(parts)


def text_for_audio(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def filter_blocks(blocks: list[HymnBlock], query: str) -> list[HymnBlock]:
    q = query.strip().lower()
    if not q:
        return blocks

    out: list[HymnBlock] = []
    for block in blocks:
        plain = " ".join([block.heading, block.heading2, block.body]).lower()
        if q in plain:
            out.append(block)
    return out


# ----------------------------
# Styling
# ----------------------------
icon_b64 = file_to_base64(ICON) if ICON.exists() else ""

st.markdown(
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .block-container {{
        padding: 0.5rem 0.8rem;
        max-width: 100%;
    }}

    .app-bar {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.8rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #4338ca, #6366f1);
        color: white;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
        margin-bottom: 0.6rem;
    }}

    .app-left {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .app-icon {{
        width: 40px;
        height: 40px;
        border-radius: 10px;
        object-fit: cover;
        background: rgba(255,255,255,0.12);
    }}

    .app-title {{
        font-size: 1.18rem;
        font-weight: 800;
        line-height: 1.15;
    }}

    .title-card {{
        margin-top: 0.4rem;
        padding: 0.9rem 1rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(128, 128, 128, 0.18);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }}

    .title-text {{
        font-size: 1.18rem;
        font-weight: 800;
        line-height: 1.5;
    }}

    .meta-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.45rem 0 0.2rem 0;
        gap: 0.5rem;
    }}

    .meta-left {{
        font-size: 0.95rem;
        font-weight: 700;
        opacity: 0.85;
    }}

    .meta-right {{
        font-size: 0.9rem;
        opacity: 0.75;
        font-weight: 600;
    }}

    .section-label {{
        margin: 1rem 0 0.45rem 0;
        font-size: 1rem;
        font-weight: 800;
        opacity: 0.9;
    }}

    .content-card {{
        margin-top: 0.4rem;
        padding: 0.95rem;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid rgba(128, 128, 128, 0.18);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        max-width: 720px;
        margin-left: auto;
        margin-right: auto;
    }}

    .hymn-card {{
        padding: 1rem 1.2rem;
        margin-bottom: 0.95rem;
        border-bottom: 1px solid rgba(128, 128, 128, 0.18);
    }}

    .hymn-card.highlight {{
        border-radius: 16px;
        background: rgba(99, 102, 241, 0.08);
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }}

    .heading {{
        color: #d32f2f;
        font-size: 1.22rem;
        font-weight: 800;
        line-height: 1.5;
        margin: 0 0 0.75rem 0;
    }}

    .heading2 {{
        color: #f57c00;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.5;
        margin: 0 0 0.65rem 0;
    }}

    .verse {{
        color: #1f2937;
        font-size: 1.03rem;
        line-height: 2.05;
        padding-left: 0.2rem;
        white-space: pre-wrap;
        margin: 0 0 0.7rem 0;
        font-family: inherit;
    }}

    .section-gap {{
        height: 0.55rem;
    }}

    .hymn-footer-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.75rem;
        margin-top: 0.65rem;
    }}

    .hymn-no {{
        font-size: 0.88rem;
        font-weight: 700;
        opacity: 0.8;
    }}

    .footer-note {{
        margin-top: 1rem;
        text-align: center;
        font-size: 0.88rem;
        opacity: 0.78;
    }}

    .empty-note {{
        margin-top: 0.6rem;
        font-size: 0.95rem;
        opacity: 0.8;
    }}

    @media (prefers-color-scheme: dark) {{
        .title-card,
        .content-card {{
            background: rgba(17, 24, 39, 0.96);
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);
        }}

        .verse {{
            color: #e5e7eb;
        }}

        .meta-left,
        .meta-right,
        .section-label,
        .hymn-no,
        .footer-note,
        .empty-note {{
            color: #cbd5e1;
        }}

        .hymn-card.highlight {{
            background: rgba(99, 102, 241, 0.16);
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header
# ----------------------------
st.markdown(
    f"""
    <div class="app-bar">
        <div class="app-left">
            {"<img src='data:image/png;base64," + icon_b64 + "' class='app-icon' alt='icon'>" if icon_b64 else ""}
            <div class="app-title">நித்யானுசந்தானம்</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Controls
# ----------------------------
col1, col2 = st.columns([4, 1])

with col1:
    query = st.text_input(
        "🔍 தேடல்",
        placeholder="தேடல்...",
        value=st.session_state.search_query,
        label_visibility="collapsed",
    )
    st.session_state.search_query = query

with col2:
    with st.popover("📚"):
        selected_section = st.selectbox(
            "உள்ளடக்கம்",
            SECTION_OPTIONS,
            index=SECTION_OPTIONS.index(st.session_state.selected_section),
            label_visibility="collapsed",
        )
        if selected_section != st.session_state.selected_section:
            st.session_state.selected_section = selected_section
            st.query_params["section"] = selected_section
            if "pasuram" in st.query_params:
                del st.query_params["pasuram"]
            st.rerun()

# ----------------------------
# Load and parse section
# ----------------------------
section_text = load_text(st.session_state.selected_section)
section = parse_section(section_text)

display_title = section.title or st.session_state.selected_section

visible_taniyans = filter_blocks(section.taniyans, st.session_state.search_query)
visible_pasurams = filter_blocks(section.pasurams, st.session_state.search_query)
visible_blocks = visible_taniyans + visible_pasurams

if not visible_blocks:
    st.markdown(
        f"""
        <div class="title-card">
            <div class="title-text">{html.escape(display_title)}</div>
        </div>
        <div class="empty-note">முடிவு எதுவும் கிடைக்கவில்லை.</div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ----------------------------
# Title
# ----------------------------
st.markdown(
    f"""
    <div class="title-card">
        <div class="title-text">{html.escape(display_title)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="meta-row">
        <div class="meta-left">{len(visible_taniyans)} தனியன்கள் · {len(visible_pasurams)} பாசுரங்கள்</div>
        <div class="meta-right">{st.session_state.selected_section}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Taniyans
# ----------------------------
if visible_taniyans:
    st.markdown('<div class="section-label">தனியன்கள்</div>', unsafe_allow_html=True)

    for block in visible_taniyans:
        card_html = '<div class="content-card hymn-card">' + render_block(block) + '</div>'
        st.markdown(card_html, unsafe_allow_html=True)

# ----------------------------
# Pasurams
# ----------------------------
if visible_pasurams:
    st.markdown('<div class="section-label">பாசுரங்கள்</div>', unsafe_allow_html=True)

    total_pasurams = len(section.pasurams)

    for block in visible_pasurams:
        highlighted = target_pasuram_no == block.original_no
        share_url = (
            f"?section={urllib.parse.quote(st.session_state.selected_section)}"
            f"&pasuram={block.original_no}"
        )

        card_html = (
            '<div class="content-card hymn-card'
            + (' highlight' if highlighted else '')
            + '">'
            + render_block(block)
            + '</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        f1, f2 = st.columns([1, 4])
        with f1:
            st.markdown(
                f'<div class="hymn-no">{block.original_no} / {total_pasurams}</div>',
                unsafe_allow_html=True,
            )
        with f2:
            st.link_button(
                "Share this pasuram",
                share_url,
                key=f"share_{st.session_state.selected_section}_{block.original_no}",
            )

# ----------------------------
# Audio
# ----------------------------
audio_text = text_for_audio(
    "\n\n".join(
        [
            display_title,
            *[
                "\n".join(filter(None, [b.heading, b.heading2, b.body]))
                for b in visible_blocks
            ],
        ]
    )
)

if st.button("🔊 கேட்க", use_container_width=True):
    try:
        with st.spinner("ஆடியோ உருவாக்கப்படுகிறது..."):
            tts = gTTS(audio_text, lang="ta")
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.audio(audio_fp.getvalue(), format="audio/mp3")
    except Exception:
        st.error("ஆடியோ உருவாக்க முடியவில்லை. இணைய இணைப்பு சரியாக உள்ளதா என்று பார்க்கவும்.")

# ----------------------------
# Footer
# ----------------------------
st.markdown(
    """
    <div class="footer-note">
        Effort by <a href="https://www.NirmalamGroup.in" target="_blank" rel="noopener noreferrer">www.NirmalamGroup.in</a>
    </div>
    """,
    unsafe_allow_html=True,
)