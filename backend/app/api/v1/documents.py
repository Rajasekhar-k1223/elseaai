import io
import os
import uuid
import json
from datetime import datetime
from typing import Optional

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, require_role
from app.db.database import async_session
from app.db.mongodb import mongodb
from app.models.document import DocumentMetadata
from app.models.user import User
from app.services.document_processing import DocumentProcessingService
from app.services.healthcare import HealthcareService
from app.worker.tasks import process_document_task

router = APIRouter()

ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".txt", ".md", ".json", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
ALLOWED_DOCUMENT_TYPES = {"general", "clinical"}

class ReviewRequest(BaseModel):
    action: str
    notes: Optional[str] = None

class FineTuneRequest(BaseModel):
    include_sections: Optional[bool] = True

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    upload_type: str = Form("general"),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    filename = file.filename or "uploaded_file"
    extension = os.path.splitext(filename)[1].lower()
    document_type = upload_type.lower() if upload_type else "general"
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        document_type = "general"

    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Supported file types: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}"
        )

    handwriting_detected = False
    if extension == ".pdf":
        text = ""
        document = fitz.open(stream=content, filetype="pdf")
        for page in document:
            text += page.get_text() + "\n"
        document.close()

        pdf_has_images = DocumentProcessingService.pdf_contains_images(content)
        ocr_text = ""
        ocr_handwriting = False
        if not text.strip() or pdf_has_images:
            ocr_text, ocr_handwriting = DocumentProcessingService.ocr_pdf_text(content)
            if not text.strip():
                text = ocr_text

        handwriting_detected = ocr_handwriting or (pdf_has_images and not text.strip())
    elif extension in IMAGE_EXTENSIONS:
        # Handle direct image uploads (scanned pages, photos)
        try:
            from PIL import Image as PILImage
            image = PILImage.open(io.BytesIO(content))
            text = DocumentProcessingService.ocr_image_text(image)
            confidence = DocumentProcessingService.ocr_image_confidence(image)
            handwriting_detected = (not text.strip()) or confidence < 50
        except Exception:
            text = ""
    elif extension == ".json":
        decoded = content.decode("utf-8", errors="ignore")
        parsed = HealthcareService.parse_fhir_resource(decoded)
        if parsed.get("error"):
            text = decoded
        else:
            lines = []
            for key, value in parsed.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                lines.append(f"{key}: {value}")
            text = "\n".join(lines)
    elif extension == ".docx":
        try:
            doc = DocxDocument(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            text = ""
    else:
        text = content.decode("utf-8", errors="ignore")

    document_id = str(uuid.uuid4())
    original_file_path = DocumentProcessingService.save_original_file(document_id, content, filename)

    raw_record = {
        "document_id": document_id,
        "user_id": current_user.id,
        "filename": filename,
        "content_type": file.content_type,
        "document_type": document_type,
        "handwriting_detected": handwriting_detected,
        "raw_text": text,
        "metadata": {
            "filename": filename,
            "content_type": file.content_type,
            "uploaded_at": datetime.utcnow().isoformat(),
            "document_type": document_type,
            "handwriting_detected": handwriting_detected,
        },
        "created_at": datetime.utcnow(),
    }
    await mongodb.db.raw_documents.insert_one(raw_record)

    cleaned_text = DocumentProcessingService.mask_and_clean_text(text)
    sections = DocumentProcessingService.detect_sections(cleaned_text)

    cleaned_record = {
        "document_id": document_id,
        "user_id": current_user.id,
        "filename": filename,
        "content_type": file.content_type,
        "document_type": document_type,
        "handwriting_detected": handwriting_detected,
        "cleaned_text": cleaned_text,
        "sections": sections,
        "created_at": datetime.utcnow(),
    }
    await mongodb.db.cleaned_documents.insert_one(cleaned_record)

    async with async_session() as session:
        document_metadata = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            content_type=file.content_type,
            document_type=document_type,
            handwriting_detected=handwriting_detected,
            user_id=current_user.id,
            original_file_path=original_file_path,
            status="pending_review"
        )
        session.add(document_metadata)
        await session.commit()
        await session.refresh(document_metadata)

    metadata_payload = {
        "filename": filename,
        "content_type": file.content_type,
        "original_file_path": original_file_path,
        "user_id": current_user.id,
        "document_type": document_type,
    }
    process_document_task.delay(document_id, cleaned_text, metadata_payload)

    return {"message": "Document uploaded and queued for processing", "document_id": document_id}

@router.get("/pending-review")
async def get_pending_review(current_user: User = Depends(get_current_user)):
    async with async_session() as session:
        query = select(DocumentMetadata)
        if not current_user.role or current_user.role.name != "Super Admin":
            query = query.filter(DocumentMetadata.user_id == current_user.id)
        result = await session.execute(query)
        documents = result.scalars().all()

    return [
        {
            "document_id": doc.document_id,
            "filename": doc.filename,
            "document_type": getattr(doc, "document_type", "general"),
            "handwriting_detected": getattr(doc, "handwriting_detected", False),
            "status": doc.status,
            "fine_tune_dataset_path": doc.fine_tune_dataset_path,
            "approved_at": doc.approved_at,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
        }
        for doc in documents
    ]

@router.post("/{document_id}/generate-finetune")
async def generate_fine_tune_dataset(
    document_id: str,
    request: FineTuneRequest,
    current_user: User = Depends(get_current_user)
):
    cleaned_doc = await mongodb.db.cleaned_documents.find_one({"document_id": document_id})
    if not cleaned_doc:
        raise HTTPException(status_code=404, detail="Cleaned document not found")
    if cleaned_doc["user_id"] != current_user.id and (not current_user.role or current_user.role.name != "Super Admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    sections = cleaned_doc.get("sections", [])
    cleaned_text = cleaned_doc.get("cleaned_text", "")
    dataset_path = DocumentProcessingService.export_fine_tune_dataset(document_id, cleaned_text, sections if request.include_sections else [])

    await mongodb.db.fine_tune_datasets.insert_one({
        "document_id": document_id,
        "user_id": current_user.id,
        "dataset_path": dataset_path,
        "status": "generated",
        "created_at": datetime.utcnow(),
    })

    async with async_session() as session:
        result = await session.execute(select(DocumentMetadata).filter(DocumentMetadata.document_id == document_id))
        doc = result.scalars().first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document metadata not found")
        doc.fine_tune_dataset_path = dataset_path
        doc.status = "dataset_generated"
        await session.commit()

    return {"message": "Fine-tune dataset generated", "dataset_path": dataset_path}

@router.post("/{document_id}/review")
async def review_document(
    document_id: str,
    review: ReviewRequest,
    current_user: User = Depends(require_role(["Super Admin", "Healthcare Analyst"]))
):
    action = review.action.lower()
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    async with async_session() as session:
        result = await session.execute(select(DocumentMetadata).filter(DocumentMetadata.document_id == document_id))
        doc = result.scalars().first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document metadata not found")

        doc.status = "approved" if action == "approve" else "rejected"
        doc.review_notes = review.notes
        if action == "approve":
            doc.approved_at = datetime.utcnow()
        await session.commit()

    return {
        "document_id": document_id,
        "status": doc.status,
        "review_notes": doc.review_notes,
        "approved_at": doc.approved_at,
    }
