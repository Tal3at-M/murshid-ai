import os
import streamlit as st
from groq import Groq
from src.engine import get_murshid_chain

st.set_page_config(
    page_title="Murshid AI | المنظومة الأكاديمية الذكية لكليات الجامعة",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 50%, #111e38 100%);
        color: #f8fafc;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.03);
        padding: 8px 12px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    [data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. تحميل الموارد
@st.cache_resource
def load_resources():
    chain = get_murshid_chain()
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return chain, groq_client

try:
    rag_chain, groq_client = load_resources()
except Exception as e:
    st.error(f"خطأ في تهيئة النظام: {e}")
    st.stop()

# 3. إدارة الـ State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""
if "rec_reset_counter" not in st.session_state:
    st.session_state.rec_reset_counter = 0

# 4. الشريط الجانبي واختيار الكلية
with st.sidebar:
    st.markdown("### 🏛️ جامعة الريادة للعلوم والتكنولوجيا")
    
    # محدد الكلية
    selected_faculty = st.selectbox(
        "اختر الكلية المستهدفة:",
        ["كلية الحاسبات والذكاء الاصطناعي", "كلية العلاج الطبيعي", "كلية التمريض"],
        index=0
    )
    
    if selected_faculty == "كلية الحاسبات والذكاء الاصطناعي":
        st.info("📌 **اللائحة المعتمدة:** الساعات المعتمدة (135 ساعة للتخرج - 4 سنوات)")
    elif selected_faculty == "كلية العلاج الطبيعي":
        st.info("📌 **اللائحة المعتمدة:** 197 ساعة معتمدة (5 سنوات) + 12 شهراً امتياز إلزامي")
    else:
        st.info("📌 **اللائحة المعتمدة:** نظام الساعات المعتمدة والتدريب الإكلينيكي")

    st.markdown("---")
    if st.button("🗑️ مسح المحادثة وتصفير الجلسة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.voice_text = ""
        st.session_state.rec_reset_counter += 1
        st.rerun()

# 5. التبويبات
tab_chat, tab_courses, tab_simulator = st.tabs([
    "💬 المستشار الأكاديمي الذكي", 
    "📚 مسار المقررات التخصصية", 
    "⚖️ محاكي الإنذارات والعبء الفصلي"
])

query_to_execute = None

# ----------------- التبويب 1: الشات والصوت -----------------
with tab_chat:
    st.markdown(f"### 🎓 مُرشد (Murshid AI) — {selected_faculty}")
    st.caption("الوكيل الأكاديمي الذكي المعتمد للوائح والتسجيل ونظم الامتحانات")
    
    st.write("⚡ **استفسارات سريعة بنقرة واحدة:**")
    c1, c2, c3, c4 = st.columns(4)
    
    if selected_faculty == "كلية الحاسبات والذكاء الاصطناعي":
        if c1.button("📊 كم ساعة للتخرج وشروط القبول؟", use_container_width=True):
            query_to_execute = "ما هو إجمالي عدد الساعات المعتمدة المطلوبة للتخرج في كلية الحاسبات والذكاء الاصطناعي وما هو الحد الأدنى للقبول؟"
        if c2.button("⚠️ معدلي 1.8 كم أسجل؟", use_container_width=True):
            query_to_execute = "في كلية الحاسبات، معدلي التراكمي 1.8، كم عدد الساعات المسموح لي بتسجيلها في الفصل الدراسي وما موقفي؟"
        if c3.button("📚 مواد الترم الأول لسنة أولى", use_container_width=True):
            query_to_execute = "ما هي المقررات الدراسية المقررة في الفصل الدراسي الأول للسنة الأولى في كلية الحاسبات وما ساعاتها؟"
        if c4.button("🎓 شروط مشروع التخرج", use_container_width=True):
            query_to_execute = "ما هي الشروط وعدد الساعات المطلوبة لتسجيل مشروع التخرج في كلية الحاسبات؟"
            
    elif selected_faculty == "كلية العلاج الطبيعي":
        if c1.button("🏥 شروط وساعات سنة الامتياز", use_container_width=True):
            query_to_execute = "ما هي مدة وساعات تدريب سنة الامتياز الإلزامية في كلية العلاج الطبيعي وما هي الأقسام ونسب الغياب المسموحة؟"
        if c2.button("⚖️ سقف الساعات والإنذار (197h)", use_container_width=True):
            query_to_execute = "في كلية العلاج الطبيعي، ما هو الحد الأقصى والأدنى للعبء الدراسي الفصلي وما ضوابط إنذار الطالب عند انخفاض المعدل؟"
        if c3.button("📚 مواد المستوى الأول (خريف)", use_container_width=True):
            query_to_execute = "ما هي مقررات المستوى الأول (فصل الخريف) في كلية العلاج الطبيعي وما هي متطلباتها؟"
        if c4.button("🩺 أقسام الكلية والدرجة الممنوحة", use_container_width=True):
            query_to_execute = "ما هي الأقسام الأكاديمية في كلية العلاج الطبيعي والدرجة العلمية التي تمنحها الكلية؟"
            
    else:  # كلية التمريض
        if c1.button("🩺 شروط التخرج والتدريب", use_container_width=True):
            query_to_execute = "ما هي متطلبات التخرج وساعات التدريب الإكلينيكي في كلية التمريض؟"
        if c2.button("📊 ضوابط التسجيل والعبء", use_container_width=True):
            query_to_execute = "ما هي ضوابط العبء الدراسي والإنذار الأكاديمي في كلية التمريض؟"
        if c3.button("📚 مقررات المستوى الأول", use_container_width=True):
            query_to_execute = "ما هي مقررات السنة الأولى في كلية التمريض؟"
        if c4.button("💰 المصروفات وشروط القيد", use_container_width=True):
            query_to_execute = "ما هي شروط القبول والمصروفات الدراسية لكلية التمريض؟"

    # الميكروفون
    with st.expander("🎙️ تحدث صوتياً (تسجيل - مراجعة - تعديل قبل الإرسال)"):
        audio_clip = st.audio_input("اضغط للتسجيل:", key=f"rec_{st.session_state.rec_reset_counter}")
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            if st.button("📝 تفريغ الصوت المسجل إلى نص", use_container_width=True):
                if audio_clip is not None:
                    with st.spinner("جاري المعالجة الصوتية عبر Whisper..."):
                        try:
                            transcript = groq_client.audio.transcriptions.create(
                                model="whisper-large-v3",
                                file=("voice.wav", audio_clip.getvalue()),
                                language="ar",
                                prompt="كلية الحاسبات والذكاء الاصطناعي، كلية العلاج الطبيعي، كلية التمريض، ساعات معتمدة، سنة الامتياز، تشريح، علاج مائي، إنذار أكاديمي"
                            )
                            st.session_state.voice_text = transcript.text
                            st.rerun()
                        except Exception as err:
                            st.error(f"خطأ في الاتصال بالنموذج الصوتي: {err}")
                else:
                    st.warning("يرجى تسجيل مقطع صوتي أولاً.")

        if st.session_state.voice_text:
            st.markdown("---")
            edited_prompt = st.text_input("راجع النص وعدّله يدوياً إذا رغبت:", value=st.session_state.voice_text)
            sc1, sc2 = st.columns([2, 1])
            with sc1:
                if st.button("🚀 إرسال السؤال إلى مُرشد", use_container_width=True):
                    query_to_execute = f"بخصوص {selected_faculty}: {edited_prompt}"
                    st.session_state.voice_text = ""
                    st.session_state.rec_reset_counter += 1
            with sc2:
                if st.button("❌ إلغاء الصوت", use_container_width=True):
                    st.session_state.voice_text = ""
                    st.session_state.rec_reset_counter += 1
                    st.rerun()

    # عرض الرسائل
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📄 المراجع المعتمدة من اللائحة"):
                    for s in msg["sources"]:
                        st.write(f"• **{s}**")

# ----------------- التبويب 2: المقررات -----------------
with tab_courses:
    if selected_faculty == "كلية الحاسبات والذكاء الاصطناعي":
        st.markdown("### 🗺️ مسار المقررات الأساسية (كلية الحاسبات والذكاء الاصطناعي)")
        st.table([
            {"المقرر": "برمجة متقدمة (CCS121)", "المتطلب السابق": "مقدمة البرمجة (CCS120)", "المستوى": "الأول - ربيع"},
            {"المقرر": "هياكل البيانات (CCS222)", "المتطلب السابق": "برمجة متقدمة (CCS121)", "المستوى": "الثاني - خريف"},
            {"المقرر": "الخوارزميات (CCS223)", "المتطلب السابق": "هياكل البيانات (CCS222)", "المستوى": "الثاني - ربيع"},
            {"المقرر": "الذكاء الاصطناعي (CAI301)", "المتطلب السابق": "الخوارزميات (CCS223)", "المستوى": "الثالث - خريف"},
            {"المقرر": "مشروع التخرج 1 (CCS460)", "المتطلب السابق": "اجتياز 85 ساعة بنجاح", "المستوى": "الرابع - خريف"},
        ])
    elif selected_faculty == "كلية العلاج الطبيعي":
        st.markdown("### 🗺️ مسار المقررات الإكلينيكية (كلية العلاج الطبيعي - 197 ساعة)")
        st.table([
            {"المقرر": "العوامل الفيزيائية الكهربائية 1 (BAS107)", "المتطلب السابق": "طبيعة حيوية + وظائف أعضاء 1", "المستوى": "الأول - ربيع"},
            {"المقرر": "تمرينات علاجية 1 (BAS108)", "المتطلب السابق": "تشريح 1 (BAS103)", "المستوى": "الأول - ربيع"},
            {"المقرر": "علاج طبيعي لأمراض القلب والصدر (INT304)", "المتطلب السابق": "تمرينات 2 + أجهزة كهربية 2", "المستوى": "الثالث - خريف"},
            {"المقرر": "علاج طبيعي لأمراض العظام وجراحتها (ORT402)", "المتطلب السابق": "تشريح 1 و 2 + تمرينات علاجية 2", "المستوى": "الرابع - خريف"},
            {"المقرر": "سنة التدريب الإكلينيكي (الامتياز)", "المتطلب السابق": "اجتياز 197 ساعة معتمدة بالكامل", "المستوى": "12 شهراً = 1728 ساعة"},
        ])
    else:
        st.markdown("### 🗺️ المقررات السريرية الأساسية (كلية التمريض)")
        st.info("يتم استرجاع شجرة المقررات وساعات التدريب السريري من لائحة التمريض المعتمدة.")

# ----------------- التبويب 3: المحاكي -----------------
with tab_simulator:
    st.markdown(f"### ⚖️ حاسبة العبء الأكاديمي — {selected_faculty}")
    sim_cgpa = st.slider("اختر المعدل التراكمي (CGPA):", 0.0, 4.0, 1.80, 0.05)
    
    if selected_faculty == "كلية العلاج الطبيعي":
        if sim_cgpa >= 3.5:
            st.success(f"**المعدل ({sim_cgpa}): متفوق جداً**\n\n• الحد النظامي: **21 ساعة معتمدة**، ويجوز رفعه إلى **24 ساعة** بموافقة مجلس الكلية.")
        elif sim_cgpa >= 2.0:
            st.info(f"**المعدل ({sim_cgpa}): وضع أكاديمي منتظم**\n\n• الحد الأقصى للتسجيل: **21 ساعة معتمدة** (الحد الأدنى 12 ساعة).")
        else:
            st.error(f"**المعدل ({sim_cgpa}): إنذار أكاديمي**\n\n• يُخفض العبء الدراسي إلى الحد الأدنى: **12 ساعة معتمدة فقط**.")
    else:
        if sim_cgpa >= 3.0:
            st.success(f"**المعدل ({sim_cgpa}): ممتاز**\n\n• الحد النظامي: **18 ساعة** (ويجوز حتى **21 ساعة** بموافقة الكلية).")
        elif sim_cgpa >= 2.0:
            st.info(f"**المعدل ({sim_cgpa}): منتظم**\n\n• الحد الأقصى: **18 ساعة معتمدة**.")
        elif sim_cgpa >= 1.0:
            st.warning(f"**المعدل ({sim_cgpa}): إنذار أول**\n\n• الحد الأقصى: **15 ساعة فقط**.")
        else:
            st.error(f"**المعدل ({sim_cgpa}): تعثر أكاديمي مشدد**\n\n• الحد الأقصى: **12 ساعة فقط**.")

# 6. الإدخال المكتوب
typed_input = st.chat_input("اطرح استفسارك الأكاديمي هنا...")
if typed_input:
    query_to_execute = f"بخصوص {selected_faculty}: {typed_input}"

# 7. التنفيذ
if query_to_execute:
    st.session_state.messages.append({"role": "user", "content": query_to_execute})
    with tab_chat:
        with st.chat_message("user"):
            st.write(query_to_execute)

        with st.chat_message("assistant"):
            with st.spinner("جاري استرجاع اللائحة الرسمية..."):
                response = rag_chain.invoke({"input": query_to_execute})
                answer = response["answer"]
                
                raw_sources = response.get("context", [])
                sources_list = []
                for s in raw_sources:
                    faculty_src = s.metadata.get("faculty") or s.metadata.get("source") or "اللائحة المعتمدة"
                    if faculty_src not in sources_list:
                        sources_list.append(faculty_src)

                st.write(answer)
                if sources_list:
                    with st.expander("📄 المراجع المعتمدة من اللائحة"):
                        for s in sources_list:
                            st.write(f"• **{s}**")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources_list
                })
    st.rerun()