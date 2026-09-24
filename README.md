# Murshid AI (مُرشد) 🎓
> **Autonomous On-Campus Multimodal AI Station & Precision Academic Advisory Engine**
> *GenAI for Education Hackathon 2026 — Smart Campus Track*

---

## 📌 Overview
**Murshid AI** is an enterprise-grade academic advisory engine designed for on-campus interactive kiosks and web portals. Grounded strictly in authentic university bylaws, it delivers zero-hallucination guidance on academic policies, official 2026/2027 tuition fee matrices, course prerequisite trees, and academic probation thresholds.

### 🏛️ Verified Pilot Faculties (Al Ryada University - RST):
1. **Faculty of Computers & Artificial Intelligence:** 135 Credit Hours | 85,500 EGP/yr | Prerequisite chains & Math 0.
2. **Faculty of Physical Therapy:** 197 Credit Hours | 96,000 EGP/yr | 12-Month Clinical Internship (1,728 hrs).
3. **Faculty of Nursing:** 140 Credit Hours | 64,500 EGP/yr | 12-Month Rotational Internship.

---

## 🚀 Key Features
- **Zero-Hallucination Retrieval:** ChromaDB vector store with metadata isolation enforcing faculty-level boundaries.
- **Multimodal Arabic Voice:** Whisper-large-v3 speech recognition with academic terminology biasing and human-in-the-loop review.
- **Out-of-Domain Guardrails:** Semantic boundaries rejecting non-academic queries to preserve institutional trust.
- **Dynamic Advisor Simulator:** Interactive CGPA workload regulator enforcing registration caps (12h–21h).

---

## 🛠️ Tech Stack
- **Inference Engine:** `openai/gpt-oss-20b` via Groq Cloud (Zero temperature)
- **Speech Recognition:** `whisper-large-v3` via Groq Audio API
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
- **Vector Store:** ChromaDB
- **Backend:** FastAPI (Asynchronous REST API)
- **Frontend:** Responsive Glassmorphic Tailwind CSS UI

---

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone [https://github.com/Tal3at-M/murshid-ai.git](https://github.com/Tal3at-M/murshid-ai.git)
cd murshid-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variable in .env
GROQ_API_KEY="your_groq_api_key"

# 4. Run application
python web/main_api.py

Access the application locally at: http://127.0.0.1:8000

---

## 👥 Engineering Team
- **Talaat Mohamed Talaat Mohamed Mousa** — *Team Leader & AI Systems Architect*
- **Maha Zakaria Hafez Abdelbary** — *Speech AI & Multimodal Engineer*
- **Menna Ali Mabrouk Ahmed** — *Full-Stack & UI/UX Developer*
- **Nour Waled Elsaied Mohamed** — *Data & Ingestion Specialist*
- **Aya Khaled Elsayed Abdelhamed Youssof** — *AI Evaluation & Hardware Integration Specialist*

---
© 2026 Murshid AI Team. All Rights Reserved.
