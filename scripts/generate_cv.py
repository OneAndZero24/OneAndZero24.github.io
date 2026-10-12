#!/usr/bin/env python3
"""Generate the LaTeX source and PDF of the CV from the structured data.

Sources
-------
- ``data/cv.yaml``            — profile, experience, education, skills, ...
- ``data/publications.yaml``  — merged publication list (see sync_publications.py)

Outputs
-------
- ``cv/cv.tex``        — generated LaTeX source (committed for transparency)
- ``static/cv.pdf``    — compiled CV, served by the website

Usage
-----
    python3 scripts/generate_cv.py            # generate + compile
    python3 scripts/generate_cv.py --no-pdf   # only write cv/cv.tex
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CV_YAML = ROOT / "data" / "cv.yaml"
PUBLICATIONS_YAML = ROOT / "data" / "publications.yaml"
CV_DIR = ROOT / "cv"
TEX_PATH = CV_DIR / "cv.tex"
PDF_OUT = ROOT / "static" / "cv.pdf"

LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "–": "--",
    "—": "---",
    "·": r"\textperiodcentered{}",
    "…": r"\ldots{}",
    "‘": "'",
    "’": "'",
    "“": "``",
    "”": "''",
}

URL_REPLACEMENTS = {"%": r"\%", "#": r"\#", "\\": r"\textbackslash{}"}


def esc(text) -> str:
    """Escape a string for LaTeX text mode."""
    if text is None:
        return ""
    return str(text).translate(str.maketrans(LATEX_REPLACEMENTS))


def url_esc(url: str) -> str:
    return str(url).translate(str.maketrans(URL_REPLACEMENTS))


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def rich_text(text) -> str:
    """Escape text for LaTeX but convert [label](url) into hyperlinks."""
    parts = re.split(r"(\[[^\]]+\]\([^)]+\))", str(text))
    out = []
    for part in parts:
        match = LINK_RE.fullmatch(part)
        if match:
            out.append(r"\href{%s}{%s}" % (url_esc(match.group(2)), esc(match.group(1))))
        else:
            out.append(esc(part))
    return "".join(out)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def itemize(bullets: list[str]) -> list[str]:
    lines = [r"\begin{itemize}[leftmargin=1.2em,topsep=0.5pt,itemsep=0.3pt,parsep=0pt]"]
    for bullet in bullets:
        lines.append(r"  \item " + rich_text(bullet))
    lines.append(r"\end{itemize}")
    return lines


def experience_entries(entries: list[dict]) -> list[str]:
    lines = []
    for entry in entries:
        lines.append(
            r"\noindent\textbf{%s} \hfill {\small\color{graytext} %s}\\"
            % (esc(entry["role"]), esc(entry["period"]))
        )
        lines.append(r"\textit{%s}\par" % esc(entry["org"]))
        lead = entry.get("lead")
        if lead:
            lines.append(r"\vspace{1pt}\noindent " + rich_text(" ".join(str(lead).split())) + r"\par\vspace{1pt}")
        bullets = entry.get("bullets") or []
        if bullets:
            lines.extend(itemize(bullets))
        lines.append(r"\vspace{0.5pt}")
    return lines


def publication_entries(items: list[dict]) -> list[str]:
    lines = [r"\begin{itemize}[leftmargin=1.2em,topsep=0.5pt,itemsep=1.5pt,parsep=0pt]"]
    for item in items:
        parts = [r"\item \textbf{%s}." % esc(item.get("title", ""))]
        authors = item.get("authors") or []
        if authors:
            authors_text = esc(", ".join(authors))
            if not authors_text.endswith("."):
                authors_text += "."
            parts.append(authors_text)
        venue = item.get("venue", "")
        if item.get("venue_details"):
            venue = (venue + ", " + item["venue_details"]).strip(", ")
        # Avoid duplicating "arXiv preprint" with the "(Preprint)" status label.
        if venue.strip().lower() == "arxiv preprint" and item.get("status") == "preprint":
            venue = ""
        if venue:
            parts.append(r"\textit{%s}." % esc(venue))
        if item.get("year"):
            parts.append(esc(item["year"]) + ".")
        status = item.get("status", "")
        if status not in {"published", ""} and item.get("status_label"):
            parts.append(r"({\color{graytext}%s})." % esc(item["status_label"]))
        paper = (item.get("links") or {}).get("paper")
        if paper:
            parts.append(r"[\href{%s}{paper}]" % url_esc(paper))
        lines.append(" ".join(parts))
    lines.append(r"\end{itemize}")
    return lines


def education_entries(entries: list[dict]) -> list[str]:
    lines = []
    for entry in entries:
        lines.append(
            r"\noindent\textbf{%s}, \textit{%s} \hfill {\small\color{graytext} %s}\par\vspace{2pt}"
            % (esc(entry["degree"]), esc(entry["org"]), esc(entry["period"]))
        )
    return lines


def build_tex(cv: dict, publications: dict) -> str:
    contact = cv.get("contact") or {}
    name = cv.get("name", "")
    positioning = cv.get("positioning", "")

    header = [
        r"\begin{center}",
        r"  {\Huge\bfseries %s}\\[3pt]" % esc(name),
        r"  {\large %s}" % esc(positioning),
    ]
    contact_line_bits = []
    if contact.get("email"):
        contact_line_bits.append(r"\href{mailto:%s}{%s}" % (url_esc(contact["email"]), esc(contact["email"])))
    if contact.get("phone"):
        contact_line_bits.append(esc(contact["phone"]))
    if contact.get("location"):
        contact_line_bits.append(esc(contact["location"]))
    if contact_line_bits:
        header.append(r"  \\[3pt] {\small " + r" · ".join(contact_line_bits) + "}")

    link_bits = []
    for key, label in (("github", "GitHub"), ("linkedin", "LinkedIn"), ("scholar", "Google Scholar"), ("website", "Website")):
        url = contact.get(key)
        if url:
            link_bits.append(r"{\small\href{%s}{%s}}" % (url_esc(url), label))
    if link_bits:
        header.append(r"  \\[2pt] " + r" · ".join(link_bits))
    header.append(r"\end{center}")

    body = []
    body.append(r"\vspace{-4pt}")

    if cv.get("research_interests"):
        body.append(r"\noindent\textbf{Research interests:} " + esc(cv["research_interests"].strip()))

    if cv.get("profile"):
        body.append(r"\par\vspace{4pt}\noindent " + esc(" ".join(cv["profile"].split())))

    items = publications.get("items") or []
    if items:
        body.append(r"\section*{Selected Publications}")
        body.extend(publication_entries(items))

    if cv.get("research_experience"):
        body.append(r"\section*{Research Experience}")
        body.extend(experience_entries(cv["research_experience"]))

    if cv.get("projects"):
        body.append(r"\section*{Selected Research Software}")
        for project in cv["projects"]:
            line = r"\noindent\textbf{%s}. %s" % (esc(project["name"]), esc(project["description"]))
            if project.get("url"):
                line += r" \href{%s}{%s}" % (url_esc(project["url"]), esc(project["url"]))
            body.append(line + r"\par")

    if cv.get("industry_experience"):
        body.append(r"\section*{Industry Experience}")
        body.extend(experience_entries(cv["industry_experience"]))

    if cv.get("teaching"):
        body.append(r"\section*{Teaching}")
        body.extend(experience_entries(cv["teaching"]))

    if cv.get("education"):
        body.append(r"\section*{Education}")
        body.extend(education_entries(cv["education"]))

    if cv.get("skills"):
        body.append(r"\section*{Skills}")
        for group, values in cv["skills"].items():
            text = ", ".join(values) if isinstance(values, list) else str(values)
            body.append(r"\noindent\textbf{%s:} %s\par\vspace{1pt}" % (esc(group), esc(text)))

    document = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[scaled=0.95]{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[margin=1.7cm]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\definecolor{accent}{HTML}{6A7BA2}
\definecolor{graytext}{HTML}{6C6C6C}
\definecolor{border}{HTML}{DDDDDD}
\usepackage[colorlinks=true, urlcolor=accent, linkcolor=accent, citecolor=accent]{hyperref}
\usepackage{microtype}
\linespread{0.96}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\titleformat{\section}{\normalfont\large\bfseries}{}{0pt}{}[\vspace{-0.5em}\textcolor{border}{\rule{\textwidth}{0.4pt}}]
\titlespacing*{\section}{0pt}{6pt}{2pt}
\begin{document}
%s
%s
\end{document}
""" % ("\n".join(header), "\n".join(body))

    return document


def compile_pdf(engine: str = "pdflatex") -> None:
    executable = shutil.which(engine)
    if executable is None:
        raise SystemExit(
            f"{engine} not found on PATH. Install a LaTeX distribution or run with --no-pdf."
        )
    for _ in range(2):
        result = subprocess.run(
            [executable, "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(CV_DIR), str(TEX_PATH)],
            cwd=CV_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout[-4000:])
            print(result.stderr[-2000:])
            raise SystemExit("pdflatex failed")
    shutil.copyfile(CV_DIR / "cv.pdf", PDF_OUT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-pdf", action="store_true", help="only write cv/cv.tex")
    parser.add_argument("--engine", default="pdflatex", help="LaTeX engine to use (default: pdflatex)")
    args = parser.parse_args()

    cv = load_yaml(CV_YAML)
    if not cv.get("name"):
        raise SystemExit(f"missing CV data: {CV_YAML}")

    publications = load_yaml(PUBLICATIONS_YAML)

    CV_DIR.mkdir(exist_ok=True)
    TEX_PATH.write_text(build_tex(cv, publications), encoding="utf-8")
    print(f"[cv] wrote {TEX_PATH.relative_to(ROOT)}")

    if args.no_pdf:
        return 0

    compile_pdf(args.engine)
    print(f"[cv] compiled {PDF_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
