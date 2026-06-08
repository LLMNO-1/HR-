import os
from fastapi import UploadFile, HTTPException
from app.config import UPLOAD_DIR, MAX_FILE_SIZE

# 支持的文件类型
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".doc"}


async def save_upload_file(file: UploadFile) -> str:
    """
    保存上传文件，返回文件路径。
    后续如需解析 PDF/Word，可在此扩展。
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}。支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 避免文件名冲突
    import uuid
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件超过最大限制 {MAX_FILE_SIZE // 1024 // 1024}MB")

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path


def read_text_file(file_path: str) -> str:
    """
    读取文件内容，支持 txt / md / pdf / docx。
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in {".txt", ".md"}:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    if ext == ".pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        if not text_parts:
            raise HTTPException(status_code=400, detail="PDF 文件无法提取文本内容，可能为扫描件")
        return "\n".join(text_parts)

    if ext == ".docx":
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            raise HTTPException(status_code=400, detail="Word 文件内容为空")
        return "\n".join(paragraphs)

    if ext == ".doc":
        raise HTTPException(status_code=400, detail="旧版 .doc 格式不支持，请转为 .docx 后上传")

    raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")
