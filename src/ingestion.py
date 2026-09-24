import os
import shutil
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "chroma_db_clean")

def extract_pdf_clean(pdf_path, faculty_name):
    if not os.path.exists(pdf_path):
        return []
    reader = pypdf.PdfReader(pdf_path)
    docs = []
    print(f"📄 قراءة {faculty_name} ({len(reader.pages)} صفحة)...")
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if len(text.strip()) > 20:
            docs.append(Document(
                page_content=text,
                metadata={"faculty": faculty_name, "page": i + 1, "source": os.path.basename(pdf_path)}
            ))
    return docs

def build_multi_faculty_database():
    all_documents = []
    
    # 1. ملف الخطة الدراسية الأساسي لكلية الحاسبات (Markdown)
    cs_md = os.path.join(DATA_DIR, "regulations.md")
    if os.path.exists(cs_md):
        print("📘 قراءة الخطة الدراسية المعتمدة (regulations.md)...")
        with open(cs_md, "r", encoding="utf-8") as f:
            all_documents.append(Document(
                page_content=f.read(),
                metadata={"faculty": "كلية الحاسبات والذكاء الاصطناعي", "source": "الخطة الدراسية المعتمدة"}
            ))

    # ملف الـ PDF المساعد
    cs_pdf = os.path.join(DATA_DIR, "CS_regulations.pdf")
    if not os.path.exists(cs_pdf):
        cs_pdf = os.path.join(DATA_DIR, "university_regulations.pdf")
    all_documents.extend(extract_pdf_clean(cs_pdf, "كلية الحاسبات والذكاء الاصطناعي"))

    # 2. كلية العلاج الطبيعي
    pt_pdf = os.path.join(DATA_DIR, "pt_regulations.pdf")
    all_documents.extend(extract_pdf_clean(pt_pdf, "كلية العلاج الطبيعي"))

    # 3. كلية التمريض
    nursing_pdf = os.path.join(DATA_DIR, "nursing_regulations.pdf")
    all_documents.extend(extract_pdf_clean(nursing_pdf, "كلية التمريض"))

    # تقسيم بحجم 600 حرف لتركيز المعلومة ومنع تجاوز حد الـ Tokens
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n### ", "\n## ", "\n\n", "\n"]
    )
    splits = text_splitter.split_documents(all_documents)
    print(f"📦 تم إنشاء {len(splits)} مقطعاً نصياً.")

    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print("✅ تم بناء قاعدة البيانات بنجاح!")

if __name__ == "__main__":
    build_multi_faculty_database()