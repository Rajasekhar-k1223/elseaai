import uuid
from fastapi import APIRouter, UploadFile, File, Depends
from app.worker.tasks import process_document_task
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

import fitz # PyMuPDF
import io

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    content = await file.read()
    
    text = ""
    if file.filename.endswith(".pdf"):
        # Use PyMuPDF for PDF extraction
        pdf_doc = fitz.open(stream=content, filetype="pdf")
        for page in pdf_doc:
            text += page.get_text() + "\n"
        pdf_doc.close()
    else:
        # Fallback for plain text or markdown
        text = content.decode("utf-8", errors="ignore")
    
    document_id = str(uuid.uuid4())
    metadata = {
        "filename": file.filename,
        "content_type": file.content_type
    }
    
    # Send to Celery worker for async processing
    process_document_task.delay(document_id, text, metadata)
    
    return {"message": "Document uploaded and queued for processing", "document_id": document_id}
