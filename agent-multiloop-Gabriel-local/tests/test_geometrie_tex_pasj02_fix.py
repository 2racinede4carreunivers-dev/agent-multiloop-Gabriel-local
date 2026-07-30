"""Régressions statiques du correctif pasj02/MiKTeX de l'Avant-Propos."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEX_PATH = ROOT / "theories" / "tex" / "geometrie_gabriel_savard_13.tex"


@pytest.fixture(scope="module")
def tex_bytes() -> bytes:
    return TEX_PATH.read_bytes()


@pytest.fixture(scope="module")
def tex(tex_bytes: bytes) -> str:
    return tex_bytes.decode("utf-8", errors="strict")


def _without_comments(source: str) -> str:
    r"""Retire les commentaires TeX tout en conservant les \% échappés."""
    clean_lines = []
    for line in source.splitlines():
        for index, char in enumerate(line):
            if char != "%":
                continue
            preceding_backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                preceding_backslashes += 1
                cursor -= 1
            if preceding_backslashes % 2 == 0:
                line = line[:index]
                break
        clean_lines.append(line)
    return "\n".join(clean_lines)


def _count_unescaped(source: str, token: str) -> int:
    count = 0
    for index, char in enumerate(source):
        if char != token:
            continue
        preceding_backslashes = 0
        cursor = index - 1
        while cursor >= 0 and source[cursor] == "\\":
            preceding_backslashes += 1
            cursor -= 1
        if preceding_backslashes % 2 == 0:
            count += 1
    return count


def test_utf8_strict_clean_nfc(tex_bytes: bytes, tex: str) -> None:
    """Le source reste portable entre MiKTeX et Overleaf."""
    assert not tex_bytes.startswith(b"\xef\xbb\xbf"), "BOM UTF-8 détecté"
    assert b"\r" not in tex_bytes, "CR/CRLF détecté"
    assert b"\x00" not in tex_bytes, "Octet NUL détecté"
    controls = [
        (index, char)
        for index, char in enumerate(tex)
        if unicodedata.category(char) == "Cc" and char not in {"\n", "\t"}
    ]
    assert not controls, f"Caractères de contrôle détectés : {controls[:5]}"
    assert unicodedata.normalize("NFC", tex) == tex, "Le fichier n'est pas en NFC"
    for marker in ("\ufffd", "Ã", "Â", "â€", "ðŸ"):
        assert marker not in tex, f"Mojibake probable détecté : {marker!r}"


def test_document_boundaries_and_delimiters(tex: str) -> None:
    clean = _without_comments(tex)
    commands = [line.strip() for line in clean.splitlines() if line.strip()]
    assert commands[0] == r"\documentclass[]{pasj02}"
    assert tex.rstrip().endswith(r"\end{document}")

    depth = 0
    for index, char in enumerate(clean):
        if char not in "{}":
            continue
        if _count_unescaped(clean[: index + 1], char) == _count_unescaped(
            clean[:index], char
        ):
            continue
        depth += 1 if char == "{" else -1
        assert depth >= 0, f"Accolade fermante sans ouverture à l'index {index}"
    assert depth == 0, f"Accolades déséquilibrées : profondeur finale {depth}"
    assert _count_unescaped(clean, "$") % 2 == 0, "Nombre impair de délimiteurs $"


def test_unnumberedsection_macro_is_complete_and_in_preamble(tex: str) -> None:
    macro_start = tex.index(r"\newcommand{\unnumberedsection}")
    document_start = tex.index(r"\begin{document}")
    makeatletter = tex.rfind(r"\makeatletter", 0, macro_start)
    makeatother = tex.find(r"\makeatother", macro_start)
    assert 0 <= makeatletter < macro_start < makeatother < document_start

    macro_block = tex[macro_start:makeatother]
    for required in (
        r"\phantomsection",
        r"\addcontentsline{toc}{section}{#1}",
        r"\Large\bfseries",
        r"\@afterheading",
    ):
        assert required in macro_block, f"Élément absent de la macro : {required}"


def test_first_two_starred_sections_are_replaced(tex: str) -> None:
    clean = _without_comments(tex)
    assert r"\section*{Note liminaire}" not in clean
    assert r"\section*{Avant-Propos" not in clean
    assert clean.count(r"\unnumberedsection{Note liminaire}") == 1
    assert clean.count(
        r"\unnumberedsection{Avant-Propos --- La Chair Première Géométrique}"
    ) == 1

    lines = clean.splitlines()
    note_line = next(
        index for index, line in enumerate(lines, start=1)
        if r"\unnumberedsection{Note liminaire}" in line
    )
    foreword_line = next(
        index for index, line in enumerate(lines, start=1)
        if r"\unnumberedsection{Avant-Propos" in line
    )
    assert 150 <= note_line <= 180
    assert note_line < foreword_line <= 185
    assert not any(r"\section*" in line for line in lines[144:180])


def test_no_problematic_section_pattern_after_abstract(tex: str) -> None:
    clean = _without_comments(tex)
    after_abstract = clean.split(r"\end{abstract}", maxsplit=1)[1]
    first_30_lines = "\n".join(after_abstract.splitlines()[:30])
    assert r"\section*" not in first_30_lines
    assert not re.search(
        r"\\section\*\{[^}]+\}\s*\\addcontentsline",
        first_30_lines,
        flags=re.DOTALL,
    )
    assert r"\unnumberedsection{Note liminaire}" in first_30_lines
    assert r"\unnumberedsection{Avant-Propos" in first_30_lines


def test_integral_foreword_content_is_preserved(tex: str) -> None:
    start = tex.index(r"\unnumberedsection{Note liminaire}")
    end = tex.index(r"\section{Fondements et Architecture", start)
    foreword = tex[start:end].replace("~", " ")
    required_fragments = (
        "Perelman",
        "MK 39",
        "Apocalypse Now",
        "Royal Victoria",
        "aqueduc",
        "Université Laval",
        "élite universitaire",
        "biais algorithmique",
        "haine",
        "L'Univers est au Carré",
        "Mme Gabriel",
        "v0.9.1 (HOL-corrigé)",
        "20 juillet 2026",
        "Lévis, Chaudière-Appalaches",
    )
    flattened = re.sub(r"[{}]", "", foreword)
    for fragment in required_fragments:
        assert fragment in flattened, f"Contenu de l'Avant-Propos absent : {fragment}"
