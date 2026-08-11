
import csv

from docx import Document


# ==========================================
# Extract Text From PDF
# ==========================================

def extract_text_from_pdf(file_path):
    from utils.pdf import extract_text_from_pdf as extract_pdf

    return extract_pdf(file_path)


# ==========================================
# Extract Text From TXT
# ==========================================

def extract_text_from_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


# ==========================================
# Extract Text From Markdown
# ==========================================

def extract_text_from_md(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


# ==========================================
# Extract Text From DOCX
# ==========================================

def extract_text_from_docx(file_path):

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


# ==========================================
# Extract Text From CSV
# ==========================================

def extract_text_from_csv(file_path):

    rows = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as file:

        reader = csv.reader(file)

        for row in reader:

            row_text = " | ".join(
                cell.strip()
                for cell in row
            )

            if row_text.strip():
                rows.append(row_text)

    return "\n".join(rows)


# ==========================================
# General Document Extractor
# ==========================================

def extract_text(
    file_path,
    extension
):

    extension = extension.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".md":
        return extract_text_from_md(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".csv":
        return extract_text_from_csv(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )
