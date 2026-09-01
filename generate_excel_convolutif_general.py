"""Génère le classeur Excel universel des suites A/B non typiques."""
from __future__ import annotations

from pathlib import Path
from shutil import copy2

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill


ROOT = Path(__file__).parent
ARCHIVE = ROOT / "archive" / "systeme_convolutif"
SOURCE = ARCHIVE / "systeme_convolutif_spectral_genere.xlsx"
FALLBACK_SOURCE = ARCHIVE / "systeme_convolutif_spectral.xlsx"
OUTPUT = ROOT / "systeme_convolutif_spectral_general.xlsx"
SHEET_NAME = "Reconstruction Universelle"

TITLE_FILL = PatternFill("solid", fgColor="1F4E78")
SECTION_FILL = PatternFill("solid", fgColor="D9EAF7")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")


def _style_title(cell) -> None:
    cell.fill = TITLE_FILL
    cell.font = Font(bold=True, color="FFFFFF", size=14)
    cell.alignment = Alignment(horizontal="center")


def _style_section(cell) -> None:
    cell.fill = SECTION_FILL
    cell.font = Font(bold=True)


def _set_formula(ws, row: int, label: str, formula: str, note: str = "") -> None:
    ws.cell(row, 1, label)
    ws.cell(row, 2, formula)
    ws.cell(row, 3, note)


def build_reconstruction_sheet(workbook) -> None:
    if SHEET_NAME in workbook.sheetnames:
        del workbook[SHEET_NAME]
    ws = workbook.create_sheet(SHEET_NAME)
    ws.merge_cells("A1:E1")
    ws["A1"] = "Reconstruction universelle des suites A et B - rapport non typique 1/k"
    _style_title(ws["A1"])

    ws.merge_cells("A2:E2")
    ws["A2"] = (
        "Saisir k >= 3 et des longueurs n >= 7. Toutes les formules sont algébriques "
        "et reconstruisent les coefficients depuis deux sommes, sans valeurs propres à un k."
    )
    ws["A2"].alignment = Alignment(wrap_text=True)

    ws["A4"] = "PARAMETRES A MODIFIER"
    _style_section(ws["A4"])
    inputs = [
        ("k (rapport 1/k)", 5),
        ("n1 : première somme", 10),
        ("n2 : deuxième somme distincte", 11),
        ("n cible (>= n1 pour convolution)", 14),
    ]
    for row, (label, value) in enumerate(inputs, start=5):
        ws.cell(row, 1, label)
        ws.cell(row, 2, value)
        ws.cell(row, 2).fill = INPUT_FILL
        ws.cell(row, 2).font = Font(bold=True)
    ws["C5"] = "Condition : k >= 3"
    ws["C6"] = "Conditions : n1, n2 >= 7 et n1 <> n2"

    ws["A11"] = "SOMMES DE DEPART (CONVOLUTION FORMELLE)"
    _style_section(ws["A11"])
    ws["A12"], ws["B12"], ws["C12"] = "Somme", "n1", "n2"
    _set_formula(
        ws, 13, "A",
        "=IF(OR($B$5<3,$B$6<7,$B$7<7),NA(),(1+1/$B$5+1/($B$5^3*($B$5-1)))*$B$5^$B$6-$B$5/($B$5-1))",
        "A(n) = (1 + 1/k + 1/(k^3*(k-1))) * k^n - k/(k-1)",
    )
    ws["C13"] = (
        "=IF(OR($B$5<3,$B$6<7,$B$7<7),NA(),"
        "(1+1/$B$5+1/($B$5^3*($B$5-1)))*$B$5^$B$7-$B$5/($B$5-1))"
    )
    _set_formula(
        ws, 14, "B",
        "=IF(OR($B$5<3,$B$6<7,$B$7<7),NA(),($B$5+1+1/($B$5^2*($B$5-1)))*$B$5^$B$6+($B$5^6-$B$5-$B$5^7)/($B$5-1))",
        "B(n) = (k + 1 + 1/(k^2*(k-1))) * k^n + (k^6-k-k^7)/(k-1)",
    )
    ws["C14"] = (
        "=IF(OR($B$5<3,$B$6<7,$B$7<7),NA(),"
        "($B$5+1+1/($B$5^2*($B$5-1)))*$B$5^$B$7+($B$5^6-$B$5-$B$5^7)/($B$5-1))"
    )

    ws["A17"] = "RECONSTRUCTION ALGEBRIQUE DES EQUATIONS A ET B"
    _style_section(ws["A17"])
    ws["A18"], ws["B18"], ws["C18"], ws["D18"] = "Suite", "Coefficient de k^n", "Constante", "Equation"
    _set_formula(ws, 19, "A", "=(B13-C13)/($B$5^$B$6-$B$5^$B$7)")
    ws["C19"] = "=B13-B19*$B$5^$B$6"
    ws["D19"] = '=CONCAT("A(n) = (",TEXT(B19,"0.###############"),")*k^n + (",TEXT(C19,"0.###############"),")")'
    _set_formula(ws, 20, "B", "=(B14-C14)/($B$5^$B$6-$B$5^$B$7)")
    ws["C20"] = "=B14-B20*$B$5^$B$6"
    ws["D20"] = '=CONCAT("B(n) = (",TEXT(B20,"0.###############"),")*k^n + (",TEXT(C20,"0.###############"),")")'
    ws["A22"] = "Les coefficients proviennent exclusivement des deux équations S(n1), S(n2)."

    ws["A24"] = "EVALUATION ET CONTROLE CONVOLUTIF"
    _style_section(ws["A24"])
    ws["A25"], ws["B25"], ws["C25"], ws["D25"] = (
        "Suite", "Somme reconstruite à n cible", "Somme par convolution", "Ecart",
    )
    _set_formula(ws, 26, "A", "=B19*$B$5^$B$8+C19")
    ws["C26"] = (
        "=IF($B$8<$B$6,NA(),$B$5^($B$8-$B$6)*B13+"
        "((1-$B$5)*C19)*(($B$5^($B$8-$B$6)-1)/($B$5-1)))"
    )
    ws["D26"] = "=B26-C26"
    _set_formula(ws, 27, "B", "=B20*$B$5^$B$8+C20")
    ws["C27"] = (
        "=IF($B$8<$B$6,NA(),$B$5^($B$8-$B$6)*B14+"
        "((1-$B$5)*C20)*(($B$5^($B$8-$B$6)-1)/($B$5-1)))"
    )
    ws["D27"] = "=B27-C27"
    ws["A29"] = "Convolution : S(n+1) = k*S(n) + (1-k)*constante."
    ws["A30"] = "Contrôle : les écarts doivent être nuls (à la précision Excel)."

    ws["A32"] = "RECONSTRUCTION DU PREMIER (DIGAMMA)"
    _style_section(ws["A32"])
    ws["A33"] = "Règle : Digamma = A(n) + signe*k^position ; P = (B(n)-Digamma)/k^6."
    ws["A34"], ws["B34"], ws["C34"], ws["D34"], ws["E34"] = (
        "Position", "Signe", "Digamma", "P candidat", "Entier ?",
    )
    candidate_row = 35
    for position_formula in ("$B$8-3", "$B$8-3", "$B$8-2", "$B$8-2"):
        sign = 1 if candidate_row in (35, 37) else -1
        ws.cell(candidate_row, 1, f"={position_formula}")
        ws.cell(candidate_row, 2, sign)
        ws.cell(candidate_row, 3, f"=B26+B{candidate_row}*$B$5^A{candidate_row}")
        ws.cell(candidate_row, 4, f"=(B27-C{candidate_row})/$B$5^6")
        ws.cell(candidate_row, 5, f'=IF(D{candidate_row}=INT(D{candidate_row}),"Oui","Non")')
        candidate_row += 1

    for column, width in {"A": 34, "B": 25, "C": 28, "D": 50, "E": 15}.items():
        ws.column_dimensions[column].width = width
    for row in (2, 22, 29, 30, 33):
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        ws.cell(row, 1).alignment = Alignment(wrap_text=True)
    ws.freeze_panes = "A5"


def main() -> None:
    source = SOURCE if SOURCE.exists() else FALLBACK_SOURCE
    if not source.exists():
        raise FileNotFoundError(f"Classeur source introuvable : {source}")
    copy2(source, OUTPUT)
    workbook = load_workbook(OUTPUT)
    build_reconstruction_sheet(workbook)
    workbook.calculation.fullCalcOnLoad = True
    workbook.calculation.forceFullCalc = True
    workbook.save(OUTPUT)
    print(f"Classeur créé : {OUTPUT}")


if __name__ == "__main__":
    main()
