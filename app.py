import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import io
import os


# ── helpers ────────────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    """Parse YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?/]|$)",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"embed/([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    # treat bare 11-char string as ID
    if re.match(r"^[0-9A-Za-z_-]{11}$", url.strip()):
        return url.strip()
    return None


def seconds_to_hms(seconds: float) -> str:
    """Convert seconds → HH:MM:SS (or MM:SS if < 1 hour)."""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


def fetch_gujarati_transcript(video_id: str):
    """
    Returns (list_of_segments, language_code) or raises a descriptive exception.
    Prefers gu (Gujarati); falls back to auto-generated Gujarati (gu-orig / gu).
    """
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try manually created Gujarati first, then auto-generated
    for generated in (False, True):
        for t in transcript_list:
            if t.language_code.startswith("gu") and t.is_generated == generated:
                return t.fetch(), t.language_code

    raise NoTranscriptFound(
        video_id,
        ["gu"],
        transcript_list._manually_created_transcripts | transcript_list._generated_transcripts,
    )


def ends_sentence(text: str) -> bool:
    """
    Return True if `text` ends at a natural sentence boundary.
    Covers Latin punctuation (. ? !) and the Gujarati/Devanagari purna virama (।).
    Trailing whitespace is ignored.
    """
    return bool(re.search(r'[.?!।]\s*$', text.strip()))


def group_segments(segments, interval_seconds: int = 900):
    """
    Group transcript segments into chunks, targeting `interval_seconds` per chunk.

    Smart boundary logic:
      1. Once the accumulated duration >= interval, we look for the first
         subsequent segment whose text ends with sentence-final punctuation
         (. ? ! or Gujarati । ) and close the chunk there.
      2. If no sentence boundary is found within a grace window (25 % extra time),
         we close at the next segment boundary — so we always split between
         whole segments, never mid-word.
    """
    GRACE_FACTOR = 1.25          # allow up to 25 % overtime to find a sentence end
    groups: list[dict] = []
    current_group: list = []
    group_start = 0.0
    threshold = interval_seconds  # close as soon as we hit this AND a sentence ends

    for i, seg in enumerate(segments):
        current_group.append(seg)
        elapsed = seg["start"] - group_start

        if elapsed < threshold:
            continue  # haven't reached the interval yet

        text = seg.get("text", "")

        if ends_sentence(text):
            # Clean sentence boundary — close the group here
            groups.append({"start": group_start, "segments": current_group})
            group_start = seg["start"] + seg.get("duration", 0)
            threshold = interval_seconds  # reset relative to new group start
            current_group = []

        elif elapsed >= interval_seconds * GRACE_FACTOR:
            # Grace window expired — close here anyway (whole segment, no mid-word cut)
            groups.append({"start": group_start, "segments": current_group})
            group_start = seg["start"] + seg.get("duration", 0)
            threshold = interval_seconds
            current_group = []
        # else: still within grace window, keep accumulating

    if current_group:
        groups.append({"start": group_start, "segments": current_group})

    return groups


def build_pdf(groups, video_id: str, video_url: str, lang_code: str,
              interval_minutes: int) -> bytes:
    """Render transcript groups to a PDF and return bytes."""
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # ── custom styles ──────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
    )
    timestamp_style = ParagraphStyle(
        "Timestamp",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#1a56db"),
        spaceBefore=14,
        spaceAfter=4,
        leading=14,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        spaceAfter=4,
        fontName="Helvetica",
    )

    story = []

    # ── title block ────────────────────────────────────────────────────────────
    story.append(Paragraph("YouTube Gujarati Transcript", title_style))
    story.append(Paragraph(f"Video ID: {video_id}", meta_style))
    story.append(Paragraph(f"URL: {video_url}", meta_style))
    story.append(Paragraph(f"Language code: {lang_code}", meta_style))
    story.append(Paragraph(
        f"Sections approx. every {interval_minutes} minute(s) — split at sentence boundaries", meta_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 0.3 * cm))

    # ── transcript groups ──────────────────────────────────────────────────────
    for g in groups:
        ts = seconds_to_hms(g["start"])
        story.append(Paragraph(f"[{ts}]", timestamp_style))

        # Merge all segment texts in the group into one paragraph
        text = " ".join(
            seg.get("text", "").replace("\n", " ").strip()
            for seg in g["segments"]
        )
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 0.2 * cm))

    doc.build(story)
    return buf.getvalue()


# ── Streamlit UI ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="YouTube Gujarati Transcript Extractor",
    page_icon="📄",
    layout="centered",
)

st.title("📄 YouTube Gujarati Transcript Extractor")
st.markdown(
    "Paste a YouTube URL below. If a **Gujarati auto-transcript** is available "
    "it will be downloaded and exported as a clean PDF."
)

with st.form("input_form"):
    url_input = st.text_input(
        "YouTube URL or Video ID",
        placeholder="https://www.youtube.com/watch?v=...",
    )
    interval_min = st.slider(
        "Target section length (minutes)",
        min_value=1, max_value=30, value=15, step=1,
        help="Sections will be approximately this long, but always end at a sentence boundary — never mid-word."
    )
    submitted = st.form_submit_button("Extract Transcript")

if submitted:
    url_input = url_input.strip()

    if not url_input:
        st.warning("Please enter a YouTube URL or Video ID.")
        st.stop()

    video_id = extract_video_id(url_input)
    if not video_id:
        st.error("Could not parse a valid YouTube video ID from the input.")
        st.stop()

    with st.spinner("Fetching transcript from YouTube…"):
        try:
            segments, lang_code = fetch_gujarati_transcript(video_id)
        except TranscriptsDisabled:
            st.error("❌ Transcripts are disabled for this video.")
            st.stop()
        except NoTranscriptFound:
            st.error(
                "❌ **Gujarati auto-transcript unavailable** for this video.\n\n"
                "YouTube does not provide a Gujarati (gu) transcript for this video ID. "
                "Try a different video or check if the video has Gujarati captions enabled."
            )
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

    st.success(f"✅ Gujarati transcript found (language code: `{lang_code}`). "
               f"Total segments: {len(segments)}")

    # Group and preview
    groups = group_segments(segments, interval_seconds=interval_min * 60)

    st.subheader("Preview")
    for g in groups[:5]:          # show first 5 groups only
        ts = seconds_to_hms(g["start"])
        text = " ".join(
            seg.get("text", "").replace("\n", " ").strip()
            for seg in g["segments"]
        )
        with st.expander(f"[{ts}]"):
            st.write(text)

    if len(groups) > 5:
        st.caption(f"… and {len(groups) - 5} more section(s) in the PDF.")

    # Build PDF
    with st.spinner("Generating PDF…"):
        pdf_bytes = build_pdf(
            groups,
            video_id=video_id,
            video_url=url_input,
            lang_code=lang_code,
            interval_minutes=interval_min,
        )

    st.download_button(
        label="⬇️ Download Gujarati Transcript PDF",
        data=pdf_bytes,
        file_name=f"transcript_{video_id}.pdf",
        mime="application/pdf",
    )
