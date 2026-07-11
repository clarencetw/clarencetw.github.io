#!/usr/bin/env python3
"""Build the three public résumé PDFs from one reviewable source file."""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        CondPageBreak,
        HRFlowable,
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError as exc:  # pragma: no cover - depends on local tooling
    raise SystemExit(
        "Missing PDF dependencies. Install resume/requirements.txt before running this script."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "resume" / "resume.multilingual.json"
ARTIFACT_DIR = ROOT / "output" / "pdf"
SITE_OUTPUTS = {
    "zh-tw": ROOT / "static" / "files" / "zh-tw" / "resume.pdf",
    "en": ROOT / "static" / "files" / "en" / "resume.pdf",
    "ja": ROOT / "static" / "files" / "ja" / "resume.pdf",
}

INK = colors.HexColor("#13201D")
MUTED = colors.HexColor("#53615D")
SURFACE = colors.HexColor("#F2F7F5")
TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#0F3D3E")
AMBER = colors.HexColor("#D97706")
LINE = colors.HexColor("#D5E0DC")
WHITE = colors.white


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--locale",
        choices=("all", "zh-tw", "en", "ja"),
        default="all",
        help="Locale to build. Defaults to all three.",
    )
    parser.add_argument(
        "--cjk-font",
        type=Path,
        help="Traditional Chinese font used by zh-TW and English PDFs.",
    )
    parser.add_argument(
        "--ja-font",
        type=Path,
        help="Japanese font used by the Japanese PDF.",
    )
    parser.add_argument(
        "--cjk-bold-font",
        type=Path,
        help="Semibold Traditional Chinese font used by zh-TW and English PDFs.",
    )
    parser.add_argument(
        "--ja-bold-font",
        type=Path,
        help="Semibold Japanese font used by the Japanese PDF.",
    )
    return parser.parse_args()


def first_existing(paths: list[Path | None]) -> Path | None:
    for path in paths:
        if path and path.expanduser().is_file():
            return path.expanduser()
    return None


def resolve_fonts(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    cjk_font = first_existing(
        [
            args.cjk_font,
            Path(os.environ["RESUME_CJK_FONT"]) if os.environ.get("RESUME_CJK_FONT") else None,
            ROOT / "resume" / "fonts" / "NotoSansTC-VariableFont_wght.ttf",
            Path.home() / "Library" / "Fonts" / "NotoSansTC-VariableFont_wght.ttf",
            Path("/Library/Fonts/Arial Unicode.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        ]
    )
    ja_font = first_existing(
        [
            args.ja_font,
            Path(os.environ["RESUME_JA_FONT"]) if os.environ.get("RESUME_JA_FONT") else None,
            ROOT / "resume" / "fonts" / "NotoSansJP-VariableFont_wght.ttf",
            Path.home() / "Library" / "Fonts" / "NotoSansJP-VariableFont_wght.ttf",
            Path("/Library/Fonts/Arial Unicode.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
            cjk_font,
        ]
    )
    if not cjk_font or not ja_font:
        raise SystemExit(
            "No suitable CJK font found. Pass --cjk-font and --ja-font with Unicode TTF files."
        )
    cjk_bold_font = first_existing([args.cjk_bold_font, cjk_font])
    ja_bold_font = first_existing([args.ja_bold_font, ja_font])
    return cjk_font, cjk_bold_font, ja_font, ja_bold_font


def register_text_font(path: Path, bold_path: Path, locale: str) -> tuple[str, str]:
    font_name = f"ResumeText-{locale}"
    bold_font_name = f"ResumeTextBold-{locale}"
    pdfmetrics.registerFont(TTFont(font_name, str(path)))
    pdfmetrics.registerFont(TTFont(bold_font_name, str(bold_path)))
    pdfmetrics.registerFontFamily(
        font_name,
        normal=font_name,
        bold=bold_font_name,
        italic=font_name,
        boldItalic=bold_font_name,
    )
    return font_name, bold_font_name


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def link(value: str, url: str, color: str = "#0F766E") -> str:
    return f'<link href="{esc(url)}" color="{color}">{esc(value)}</link>'


def styles_for(font_name: str, bold_font_name: str, locale: str) -> dict[str, ParagraphStyle]:
    cjk = locale in {"zh-tw", "ja"}
    body_size = 8.7 if cjk else 8.45
    body_leading = 12.1 if cjk else 11.6
    common = {
        "wordWrap": "CJK" if cjk else None,
        "splitLongWords": True,
        "allowWidows": 0,
        "allowOrphans": 0,
    }
    return {
        "name": ParagraphStyle(
            "ResumeName",
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=28,
            textColor=WHITE,
            spaceAfter=3,
        ),
        "role": ParagraphStyle(
            "ResumeRole",
            **common,
            fontName=font_name,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#D8F3ED"),
            spaceAfter=7,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            **common,
            fontName=font_name,
            fontSize=7.7,
            leading=10,
            textColor=colors.HexColor("#D8F3ED"),
        ),
        "section": ParagraphStyle(
            "ResumeSection",
            **common,
            fontName=bold_font_name,
            fontSize=9.6,
            leading=12,
            textColor=TEAL_DARK,
            spaceBefore=2,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            **common,
            fontName=font_name,
            fontSize=body_size,
            leading=body_leading,
            textColor=INK,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "ResumeSmall",
            **common,
            fontName=font_name,
            fontSize=7.8 if cjk else 7.65,
            leading=10.6 if cjk else 10.2,
            textColor=MUTED,
        ),
        "credential": ParagraphStyle(
            "ResumeCredential",
            **common,
            fontName=font_name,
            fontSize=7.55 if cjk else 7.4,
            leading=9.8 if cjk else 9.5,
            textColor=INK,
            leftIndent=8,
            firstLineIndent=-6,
            spaceAfter=0.45,
        ),
        "entry_title": ParagraphStyle(
            "ResumeEntryTitle",
            **common,
            fontName=bold_font_name,
            fontSize=9.6 if cjk else 9.45,
            leading=12.8,
            textColor=INK,
            spaceAfter=1,
        ),
        "entry_meta": ParagraphStyle(
            "ResumeEntryMeta",
            **common,
            fontName=font_name,
            fontSize=7.75,
            leading=10.1,
            textColor=MUTED,
            spaceAfter=3,
        ),
        "date": ParagraphStyle(
            "ResumeDate",
            **common,
            fontName=font_name,
            fontSize=7.5,
            leading=10,
            textColor=AMBER,
            alignment=TA_RIGHT,
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            **common,
            fontName=font_name,
            fontSize=8.25 if cjk else 8.05,
            leading=11.35 if cjk else 10.95,
            textColor=INK,
            leftIndent=9,
            firstLineIndent=-7,
            spaceAfter=1.4,
        ),
        "skill": ParagraphStyle(
            "ResumeSkill",
            **common,
            fontName=font_name,
            fontSize=7.65 if cjk else 7.45,
            leading=10.35 if cjk else 9.95,
            textColor=INK,
        ),
        "footer": ParagraphStyle(
            "ResumeFooter",
            fontName="Helvetica",
            fontSize=6.8,
            leading=8,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
    }


def section_heading(label: str, styles: dict[str, ParagraphStyle]) -> list:
    return [
        CondPageBreak(22 * mm),
        Spacer(1, 3.2 * mm),
        Paragraph(esc(label), styles["section"]),
        HRFlowable(width="100%", thickness=0.75, color=TEAL, spaceAfter=3.2 * mm),
    ]


def header_block(data: dict, shared: dict, styles: dict[str, ParagraphStyle], width: float) -> Table:
    contacts = " &nbsp; | &nbsp; ".join(
        [
            link(shared["email"], f'mailto:{shared["email"]}', "#D8F3ED"),
            link("clarence.tw", shared["website"], "#D8F3ED"),
            link("blog.clarence.tw", shared["blog"], "#D8F3ED"),
            link("GitHub", shared["github"], "#D8F3ED"),
            link("LinkedIn", shared["linkedin"], "#D8F3ED"),
        ]
    )
    table = Table(
        [
            [Paragraph(esc(shared["name"]), styles["name"])],
            [Paragraph(esc(data["title"]), styles["role"])],
            [Paragraph(contacts, styles["contact"])],
        ],
        colWidths=[width],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), TEAL_DARK),
                ("LEFTPADDING", (0, 0), (-1, -1), 7 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7 * mm),
                ("TOPPADDING", (0, 0), (-1, 0), 6 * mm),
                ("TOPPADDING", (0, 1), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 1), 0),
                ("BOTTOMPADDING", (0, 2), (-1, 2), 5.5 * mm),
            ]
        )
    )
    return table


def expertise_table(items: list[dict], styles: dict[str, ParagraphStyle], width: float) -> Table:
    cells = []
    for item in items:
        cells.append(
            Paragraph(
                f'<b><font color="#0F766E">{esc(item["name"])}</font></b><br/>{esc(item["items"])}',
                styles["skill"],
            )
        )
    rows = [cells[index : index + 2] for index in range(0, len(cells), 2)]
    table = Table(rows, colWidths=[width / 2, width / 2], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3.3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3.3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4 * mm),
            ]
        )
    )
    return table


def experience_block(item: dict, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    organization = link(item["organization"], item["url"])
    flowables = [
        Paragraph(esc(item["role"]), styles["entry_title"]),
        Paragraph(f'{organization} &nbsp; | &nbsp; <font color="#D97706">{esc(item["date"])}</font>', styles["entry_meta"]),
    ]
    flowables.extend(
        Paragraph(f'- {esc(bullet)}', styles["bullet"]) for bullet in item.get("bullets", [])
    )
    flowables.append(Spacer(1, 2.2 * mm))
    return KeepTogether(flowables)


def compact_block(item: dict, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    title = link(item["title"], item["url"])
    return KeepTogether(
        [
            Paragraph(f'{title} &nbsp; <font color="#D97706">{esc(item["date"])}</font>', styles["entry_title"]),
            Paragraph(esc(item["detail"]), styles["small"]),
            Spacer(1, 2.2 * mm),
        ]
    )


def certification_blocks(
    items: list[dict], styles: dict[str, ParagraphStyle]
) -> list[KeepTogether]:
    blocks = []
    for item in items:
        title = (
            link(item["title"], item["url"])
            if item.get("url")
            else f'<font color="#0F766E">{esc(item["title"])}</font>'
        )
        focus = ""
        if item.get("focus"):
            focus = f' &nbsp; <font color="#D97706">{esc(item["focus"])}</font>'
        flowables = [
            Paragraph(
                f'<b>{title}</b>{focus}: {esc(item["detail"])}',
                styles["small"],
            )
        ]
        flowables.extend(
            Paragraph(f'- {esc(credential)}', styles["credential"])
            for credential in item.get("credentials", [])
        )
        flowables.append(Spacer(1, 1.2 * mm))
        blocks.append(KeepTogether(flowables))
    return blocks


def education_block(item: dict, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    organization = link(item["organization"], item["url"])
    return KeepTogether(
        [
            Paragraph(esc(item["title"]), styles["entry_title"]),
            Paragraph(f'{organization} &nbsp; | &nbsp; <font color="#D97706">{esc(item["date"])}</font>', styles["entry_meta"]),
            Spacer(1, 1.6 * mm),
        ]
    )


def draw_page(canvas, doc, data: dict, shared: dict, total_pages: int) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setTitle(f'{shared["name"]} - {data["title"]}')
    canvas.setAuthor(shared["name"])
    canvas.setSubject("Public professional résumé")
    if doc.page > 1:
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(TEAL_DARK)
        canvas.drawString(doc.leftMargin, height - 22, shared["name"])
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, height - 27, width - doc.rightMargin, height - 27)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 27, width - doc.rightMargin, 27)
    canvas.setFont("Helvetica", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 16, shared["name"])
    canvas.drawCentredString(width / 2, 16, "clarence.tw")
    canvas.drawRightString(width - doc.rightMargin, 16, f"{doc.page} / {total_pages}  |  2026-07")
    canvas.restoreState()


def build_locale(
    locale: str, payload: dict, font_path: Path, bold_font_path: Path
) -> tuple[Path, Path]:
    shared = payload["shared"]
    data = payload["locales"][locale]
    font_name, bold_font_name = register_text_font(font_path, bold_font_path, locale)
    styles = styles_for(font_name, bold_font_name, locale)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact = ARTIFACT_DIR / f"clarence-lin-resume-{locale}.pdf"
    site_output = SITE_OUTPUTS[locale]
    site_output.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(artifact),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm,
        title=f'{shared["name"]} - {data["title"]}',
        author=shared["name"],
        subject="Public professional résumé",
    )
    story = [header_block(data, shared, styles, doc.width)]
    story.extend(section_heading(data["labels"]["profile"], styles))
    story.append(Paragraph(esc(data["summary"]), styles["body"]))
    story.extend(section_heading(data["labels"]["expertise"], styles))
    story.append(expertise_table(data["expertise"], styles, doc.width))
    story.extend(section_heading(data["labels"]["experience"], styles))
    story.extend(experience_block(item, styles) for item in data["experience"])

    story.append(PageBreak())
    story.extend(section_heading(data["labels"]["publicWork"], styles))
    story.extend(compact_block(item, styles) for item in data["publicWork"])
    story.extend(section_heading(data["labels"]["certifications"], styles))
    story.extend(certification_blocks(data["certifications"], styles))
    story.extend(section_heading(data["labels"]["projects"], styles))
    story.extend(compact_block(item, styles) for item in data["projects"])
    story.extend(section_heading(data["labels"]["education"], styles))
    story.extend(education_block(item, styles) for item in data["education"])
    story.extend(section_heading(data["labels"]["community"], styles))
    story.append(Paragraph(esc(data["community"]), styles["body"]))

    on_page = lambda canvas, current_doc: draw_page(canvas, current_doc, data, shared, 2)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    reader = PdfReader(str(artifact))
    if len(reader.pages) != 2:
        raise RuntimeError(f"Expected 2 pages for {locale}, got {len(reader.pages)}")
    shutil.copy2(artifact, site_output)
    return artifact, site_output


def main() -> int:
    args = parse_args()
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    cjk_font, cjk_bold_font, ja_font, ja_bold_font = resolve_fonts(args)
    locales = SITE_OUTPUTS.keys() if args.locale == "all" else [args.locale]
    for locale in locales:
        font_path = ja_font if locale == "ja" else cjk_font
        bold_font_path = ja_bold_font if locale == "ja" else cjk_bold_font
        artifact, site_output = build_locale(locale, payload, font_path, bold_font_path)
        print(f"built {locale}: {artifact.relative_to(ROOT)}")
        print(f"site  {locale}: {site_output.relative_to(ROOT)}")
        print(f"font  {locale}: {font_path}")
        print(f"bold  {locale}: {bold_font_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
