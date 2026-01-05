import re
from pathlib import Path
from collections import defaultdict
import PyPDF2

# Dateipfade definieren 

REPORT_FOLDER = Path(
    r"Beispielpfad"
)

OUTPUT_MATRIX_DIR = Path(
    r"Beispielpfad"
)

OUTPUT_COMPANY_FILE = OUTPUT_MATRIX_DIR / "Unternehmen_Gesetze.csv"
OUTPUT_YEAR_FILE = OUTPUT_MATRIX_DIR / "Berichtsjahr_Gesetze.csv"
OUTPUT_COMPANY_YEAR_FILE = OUTPUT_MATRIX_DIR / "Unternehmen_Berichtsjahr_Gesetze.csv"

# Konfiguration

OUTPUT_MATRIX_DIR.mkdir(parents=True, exist_ok=True)

# Hilfsfunktionen definieren

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extrahiert den Text aus einer PDF-Datei und gibt ihn als String zurück

    Liest alle Seiten der PDF ein, extrahiert den Text je Seite
    und fügt die Textblöcke mit Zeilenumbrüchen zusammen

    Args:
        pdf_path (Path): Pfad zur PDF-Datei

    Returns:
        str: Der extrahierte Text der PDF
    """ 
    text_chunks = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


def parse_company_and_year(pdf_path: Path):
    """
    Extrahiert Unternehmensname und Berichtsjahr aus dem PDF-Dateinamen im Format "Unternehmen YYYY.pdf"

    Args:
        pdf_path (Path): Pfad zur PDF-Datei

    Returns:
        tuple[str, str]: (company, year) mit Unternehmensname und Jahr als String

    """ 
    stem = pdf_path.stem  
    parts = stem.split(" ", 1)

    if len(parts) == 2:
        company = parts[0].strip()
        rest = parts[1]
        m = re.search(r"\d{4}", rest)
        if m:
            year = m.group(0)
        else:
            year = "Unbekannt"
    else:
       
        company = stem
        year = "Unbekannt"

    return company, year

# Kategorien und Suchwörter definieren

search_clusters = {
    "CSR-RUG": [
        "CSR-RUG",
        "CSR-Richtlinie-Umsetzungsgesetz",
        "German CSR Directive Implementation Act",
        "CSR Richtlinie Umsetzungsgesetz",
    ],
    "CSRD": [
        "CSRD",
        "2022/2464",
        "Corporate Sustainability Reporting Directive",
        "Richtlinie über die Nachhaltigkeitsberichterstattung von Unternehmen",
    ],
    "DIN EN ISO 14064-1": [
        "14064-1",
        "Spezifikation mit Anleitung zur quantitativen Bestimmung und Berichterstattung von Treibhausgasemissionen und Entzug von Treibhausgasen auf Organisationsebene",
        "Specification with guidance at the organization level for quantification and reporting of greenhouse gas emissions and removals",
        "14064 1",
    ],
    "ESRS": [
        "ESRS",
        "Europäische Standards für die Nachhaltigkeitsberichterstattung",
        "European Sustainability Reporting Standards",
        "2023/2772",
    ],
    "GHG Protocol Corporate Standard": [
        "GHG Protocol",
        "THG Protokoll",
        "GHG-Protocol",
        "Greenhouse Gas Protocol",
    ],
    "GHG Protocol Scope 2 Guidance": [
        "GHG Protocol Scope 2",
        "GHG-Protocol Scope 2",
        "Leitlinien für Scope-2-Emissionen",
        "Leitfaden der Greenhouse Gas Protocol Initiative zur Ermittlung von Scope-2-Emissionen"
    ],
    "GHG Protocol Scope 3 Guidance": [
        "GHG Protocol Technical Guidance for Calculating Scope 3 Emissions",
        "GHG Protocol Scope 3 Guidance",
        "THG Protokoll Scope 3 Leitfaden",
        "GHG Protocol Scope 3 Calculation Guidance",
    ],
    "GHG Protocol Scope 3 Standard": [
        "GHG Protocol Scope 3 Standard",
        "Corporate Value Chain (Scope 3)",
        "Corporate Value Chain Standard",
        "Scope-3-Standard",
    ],
    "GRI 1-3 Universal Standards": [
        "GRI 1",
        "GRI-Standards",
        "GRI Universelle Standards",
        "GRI Universal Standards",
    ],
    "GRI 305 Emissionen": [
        "GRI 305",
        "305-",
        "305: Emission",
        "305 Emission",
    ],
    "IFRS S1 & S2": [
        "IFRS S1",
        "IFRS S2",
        "International Financial Reporting Standards Sustainability",
        "global accounting and sustainability disclosure standards",
    ],
    "NFRD": [
        "2014/95",
        "NFRD",
        "Richtlinie über die nichtfinanzielle Berichterstattung",
        "Non-Financial Reporting Directive",
    ],
    "NFRD Leitlinien klimabezogene Berichterstattung": [
        "2019/C 209/01",
        "Leitlinien für die Berichterstatung über nichtfinanzielle Informationen: Nachtrag zur klimabezogenen Berichterstattung",
        "Guidelines on non-financial reporting: Supplement on reporting climate-related information",
        "NFRD Leitlinien klimabezogene Berichterstattung",
    ],
    "NFRD Leitlinien nichtfinanzielle Informationen": [
        "2017/C 215/01",
        "Leitlinien für die Berichterstattung über nichtfinanzielle Informationen (Methode zur Berichterstattung über nichtfinanzielle Informationen)",
        "Guidelines on non-financial reporting (methodology for reporting non-financial information)",
        "NFRD Leitlinien nichtfinanzielle Informationen",
    ],
    "Taxonomy Regulation": [
        "2020/852",
        "Taxonomie",
        "Taxonomy",
        "establishment of a framework to facilitate sustainable investment",
    ],
    "Taxonomy Regulation Delegierte Verordnung Klima": [
        "2021/2139",
        "Taxonomy Climate Delegated Act",
        "festlegung der technischen Bewertungskriterien, anhand deren bestimmt wird, unter welchen Bedingungen davon auszugehen ist, dass eine Wirtschaftstätigkeit einen wesentlichen Beitrag zum Klimaschutz oder zur Anpassung an den Klimawandel leistet, und anhand deren bestimmt wird, ob diese Wirtschaftstätigkeit erhebliche Beeinträchtigungen eines der übrigen Umweltziele vermeidet",
        "establishing the technical screening criteria for determining the conditions under which an economic activity qualifies as contributing substantially to climate change mitigation or climate change adaptation and for determining whether that economic activity causes no significant harm to any of the other environmental objectives",
    ],
    "Taxonomy Regulation Delegierte Verordnung Offenlegung": [
        "2021/2178",
        "Taxonomy Disclosures Delegated Act",
        "Festlegung des Inhalts und der Darstellung der Informationen, die von Unternehmen, die unter Artikel 19a oder Artikel 29a der Richtlinie 2013/34/EU fallen, in Bezug auf ökologisch nachhaltige Wirtschaftstätigkeiten offenzulegen sind, und durch Festlegung der Methode, anhand deren die Einhaltung dieser Offenlegungspflicht zu gewährleisten ist",
        "specifying the content and presentation of information to be disclosed by undertakings subject to Articles 19a or 29a of Directive 2013/34/EU concerning environmentally sustainable economic activities, and specifying the methodology to comply with that disclosure obligation",
    ],
}

laws = sorted(search_clusters.keys())

# Texte einlesen

report_files = sorted(REPORT_FOLDER.glob("*.pdf"))
if not report_files:
    raise FileNotFoundError(f"Im Ordner {REPORT_FOLDER} wurden keine PDF-Dateien gefunden.")

print("Gefundene Berichte:")
for pdf in report_files:
    print("  -", pdf.name)

# 5 Matrizen definieren

company_law_counts = defaultdict(lambda: defaultdict(int))

year_law_counts = defaultdict(lambda: defaultdict(int))

company_year_law_counts = defaultdict(lambda: defaultdict(int))

def normalize_for_search(s: str) -> str:
    """
    Normalisiert einen Text
    - Nur Kleinbuchstaben
    - Entfernen von Zeilenumbrüchen mit Silbentrennung
    - Reduzieren beliebiger Whitespace-Folgen auf ein einzelnes Leerzeichen
    - Entfernen führender und nachgestellter Leerzeichen

    Args:
        s (str): Eingabetext

    Returns:
        str: Normalisierter Text
    """

    s = s.lower()
    s = re.sub(r"-\s+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

prepared_search_clusters = {
    law_name: [
        normalize_for_search(kw)
        for kw in keywords
        if kw.strip()
    ]
    for law_name, keywords in search_clusters.items()
}

# Suche in Texten

print("\nDurchsuche alle Berichte nach allen SearchClustern...\n")

for pdf_path in report_files:
    company, year = parse_company_and_year(pdf_path)
    company_year_key = f"{company} {year}"

    print(f"Bericht: {pdf_path.name}  ->  Unternehmen='{company}', Jahr='{year}'")

    text = extract_text_from_pdf(pdf_path)
    text_norm = normalize_for_search(text)

    for law_name, norm_keywords in prepared_search_clusters.items():
        found = False  

        for kw_norm in norm_keywords:
            if not kw_norm:
                continue

            if kw_norm in text_norm:
                found = True
                break  

        if found:
            company_law_counts[company][law_name] = 1
            year_law_counts[year][law_name] = 1
            company_year_law_counts[company_year_key][law_name] = 1

print("\nSuche abgeschlossen.\n")

# Matrizen erzeugen

def write_matrix_csv(output_path: Path, column_keys, data_dict, row_labels):
    """
    Schreibt eine Matrix als CSV-Datei mit ; als Trennzeichen

    Die erste Spalte enthält die Zeilenlabels (Gesetzesnamen)
    Die Spalten entsprechen den Einträgen aus `column_keys` (Unternehmen, Berichtsjahr)
    Für jede Kombination wird aus `data_dict[col].get(law_name, 0)`
    ein Wert geschrieben

    Args:
        output_path (Path): Zielpfad der CSV-Datei
        column_keys (Iterable[str]): Spaltenüberschriften
        data_dict (Mapping[str, Mapping[str, int]]):
             Verschachteltes Dictionary: außen Spalten-Key (Unternehmen, Berichtsjahr), innen Gesetz (1 = gefunden, 0 = nicht gefunden)
        row_labels (Iterable[str]): Zeilenlabels

    Returns:
        None: CSV-Datei wird gespeichert

    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Gesetz;" + ";".join(column_keys) + "\n")

        for law_name in row_labels:
            row_values = []
            for col in column_keys:
                val = data_dict[col].get(law_name, 0)
                row_values.append(str(val))
            f.write(law_name + ";" + ";".join(row_values) + "\n")


companies = sorted(company_law_counts.keys())
write_matrix_csv(OUTPUT_COMPANY_FILE, companies, company_law_counts, laws)
print(f"Matrix Unternehmen x Gesetze gespeichert unter:\n  {OUTPUT_COMPANY_FILE}")

years = sorted(year_law_counts.keys())
write_matrix_csv(OUTPUT_YEAR_FILE, years, year_law_counts, laws)
print(f"Matrix Berichtsjahr x Gesetze gespeichert unter:\n  {OUTPUT_YEAR_FILE}")

company_year_keys = sorted(company_year_law_counts.keys())
write_matrix_csv(OUTPUT_COMPANY_YEAR_FILE, company_year_keys, company_year_law_counts, laws)
print(f"Matrix Unternehmen+Berichtsjahr x Gesetze gespeichert unter:\n  {OUTPUT_COMPANY_YEAR_FILE}")
