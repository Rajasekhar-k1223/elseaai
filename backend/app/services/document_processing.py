import io
import os
import re
import json
import fitz
from typing import List
from app.core.config import settings
from app.services.healthcare import HealthcareService

try:
    from PIL import Image
    import pytesseract
    from pytesseract import Output
    OCR_AVAILABLE = True
except ImportError:
    Image = None
    pytesseract = None
    Output = None
    OCR_AVAILABLE = False

class DocumentProcessingService:
    SECTION_HEADERS = [
        "history of present illness",
        "medical history",
        "past medical history",
        "clinical findings",
        "examination",
        "assessment",
        "plan",
        "diagnosis",
        "impression",
        "recommendation",
        "treatment",
        "medications",
        "allergies",
        "vital signs",
        "laboratory results"
    ]

    @staticmethod
    def save_original_file(document_id: str, content: bytes, filename: str) -> str:
        os.makedirs(settings.ORIGINAL_DOCUMENTS_DIR, exist_ok=True)
        extension = os.path.splitext(filename)[1] or ".pdf"
        path = os.path.join(settings.ORIGINAL_DOCUMENTS_DIR, f"{document_id}{extension}")
        with open(path, "wb") as file:
            file.write(content)
        return path

    @staticmethod
    def pdf_contains_images(content: bytes) -> bool:
        try:
            document = fitz.open(stream=content, filetype="pdf")
            for page in document:
                if page.get_images(full=True):
                    document.close()
                    return True
            document.close()
        except Exception:
            return False
        return False

    @staticmethod
    def pdf_page_to_image(page) -> "Image.Image | None":
        if not OCR_AVAILABLE:
            return None
        try:
            pix = page.get_pixmap(dpi=300)
            mode = "RGBA" if pix.alpha else "RGB"
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            return image
        except Exception:
            return None

    @staticmethod
    def ocr_image_text(image) -> str:
        if not OCR_AVAILABLE:
            return ""
        try:
            return pytesseract.image_to_string(image, lang="eng")
        except Exception:
            return ""

    @staticmethod
    def ocr_image_confidence(image) -> float:
        if not OCR_AVAILABLE:
            return 0.0
        try:
            data = pytesseract.image_to_data(image, output_type=Output.DICT)
            confs = [int(conf) for conf in data.get("conf", []) if conf.strip().isdigit() and int(conf) >= 0]
            if not confs:
                return 0.0
            return sum(confs) / len(confs)
        except Exception:
            return 0.0

    @staticmethod
    def ocr_pdf_text(content: bytes) -> tuple[str, bool]:
        if not OCR_AVAILABLE:
            return "", False

        try:
            document = fitz.open(stream=content, filetype="pdf")
            page_texts = []
            low_confidence_pages = 0
            image_pages = 0
            for page in document:
                image = DocumentProcessingService.pdf_page_to_image(page)
                if image is None:
                    continue
                image_pages += 1
                page_text = DocumentProcessingService.ocr_image_text(image)
                confidence = DocumentProcessingService.ocr_image_confidence(image)
                if page_text.strip():
                    page_texts.append(page_text)
                if confidence < 50:
                    low_confidence_pages += 1
            document.close()

            text = "\n".join(page_texts).strip()
            handwriting_detected = image_pages > 0 and (text == "" or low_confidence_pages >= max(1, image_pages // 2))
            return text, handwriting_detected
        except Exception:
            return "", False

    @staticmethod
    def clean_text(text: str) -> str:
        text = text.replace("\r", " ")
        text = re.sub(r"\s+\n", " \n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    @staticmethod
    def detect_sections(text: str) -> List[dict]:
        lines = text.splitlines()
        sections = []
        current_section = {"title": "General", "text": ""}

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()
            is_header = any(lower.startswith(header + ":") or lower == header for header in DocumentProcessingService.SECTION_HEADERS)
            is_generic_header = re.match(r"^[A-Z][A-Za-z0-9 ]{3,}:$", stripped) is not None

            if stripped and (is_header or is_generic_header):
                if current_section["text"].strip():
                    sections.append(current_section)
                current_section = {"title": stripped.rstrip(":"), "text": ""}
            else:
                current_section["text"] += line + "\n"

        if current_section["text"].strip():
            sections.append(current_section)

        if not sections:
            sections = [{"title": "General", "text": text.strip()}]

        return sections

    @staticmethod
    def export_fine_tune_dataset(document_id: str, cleaned_text: str, sections: List[dict]) -> str:
        os.makedirs(settings.FINE_TUNE_OUTPUT_DIR, exist_ok=True)
        path = os.path.join(settings.FINE_TUNE_OUTPUT_DIR, f"{document_id}.jsonl")

        with open(path, "w", encoding="utf-8") as output_file:
            if sections and len(sections) > 1:
                for section in sections:
                    title = section.get("title", "General")
                    text = section.get("text", "").strip()
                    if text:
                        conversation = {
                            "messages": [
                                {"role": "system", "content": "You are a helpful medical assistant."},
                                {"role": "user", "content": f"Summarize the following medical section titled {title}:"},
                                {"role": "assistant", "content": text}
                            ]
                        }
                        output_file.write(json.dumps(conversation) + "\n")
            else:
                conversation = {
                    "messages": [
                        {"role": "system", "content": "You are a helpful medical assistant."},
                        {"role": "user", "content": "Summarize the following medical document:"},
                        {"role": "assistant", "content": cleaned_text.strip()}
                    ]
                }
                output_file.write(json.dumps(conversation) + "\n")

        return path

    @staticmethod
    def mask_and_clean_text(text: str) -> str:
        masked = HealthcareService.mask_phi(text)
        return DocumentProcessingService.clean_text(masked)
