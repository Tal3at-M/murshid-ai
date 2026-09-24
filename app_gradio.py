import os
from dotenv import load_dotenv
import gradio as gr
from groq import Groq
from src.engine import get_murshid_chain

load_dotenv()

# تهيئة المحرك والعميل
rag_chain = get_murshid_chain()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. تفريغ الصوت
def transcribe_audio(audio_path, faculty):
    if not audio_path:
        return ""
    try:
        with open(audio_path, "rb") as file:
            transcript = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=("voice.wav", file.read()),
                language="ar",
                prompt=f"استفسار طالب يخص {faculty}، جامعة الريادة للعلوم والتكنولوجيا، ساعات معتمدة، سنة الامتياز، مصروفات، إنذار أكاديمي"
            )
        return transcript.text
    except Exception as e:
        return f"خطأ في معالجة الصوت: {e}"

# 2. توليد الإجابة
def respond(user_message, chat_history, faculty):
    if not user_message or not user_message.strip():
        return "", chat_history
    
    if chat_history is None:
        chat_history = []
    
    query = f"بخصوص {faculty}: {user_message.strip()}"
    response = rag_chain.invoke({"input": query})
    answer = response["answer"]
    
    raw_sources = response.get("context", [])
    sources_list = []
    for s in raw_sources:
        src = s.metadata.get("faculty") or s.metadata.get("source") or "اللائحة المعتمدة"
        if src not in sources_list:
            sources_list.append(src)
            
    if sources_list:
        answer += "\n\n---\n**📄 المراجع المعتمدة:**\n" + "\n".join([f"• {h}" for h in sources_list])
    
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": answer})
    return "", chat_history

# 3. محاكي المعدل
def simulate(cgpa, faculty):
    if faculty == "كلية العلاج الطبيعي":
        if cgpa >= 3.5:
            return f"### النتيجة: متفوق جداً ({cgpa})\n- الحد النظامي: **21 ساعة معتمدة**، ويجوز رفعه إلى **24 ساعة** بموافقة مجلس الكلية."
        elif cgpa >= 2.0:
            return f"### النتيجة: وضع أكاديمي منتظم ({cgpa})\n- الحد الأقصى للتسجيل: **21 ساعة معتمدة** (الحد الأدنى 12 ساعة)."
        else:
            return f"### النتيجة: إنذار أكاديمي ({cgpa})\n- يُخفض العبء الدراسي إلى الحد الأدنى: **12 ساعة معتمدة فقط**."
    else:
        if cgpa >= 3.0:
            return f"### النتيجة: ممتاز / متفوق ({cgpa})\n- الحد المسموح: **18 ساعة معتمدة** (ويجوز حتى **21 ساعة** بموافقة مجلس الكلية)."
        elif cgpa >= 2.0:
            return f"### النتيجة: وضع أكاديمي منتظم ({cgpa})\n- الحد المسموح: **18 ساعة معتمدة**."
        elif cgpa >= 1.0:
            return f"### النتيجة: تحت الملاحظة الأكاديمية - إنذار أول ({cgpa})\n- الحد الأقصى للتسجيل: **15 ساعة معتمدة فقط**."
        else:
            return f"### النتيجة: تعثر أكاديمي مشدد ({cgpa})\n- الحد الأقصى للتسجيل: **12 ساعة معتمدة**.\n- ⚠️ **تنبيه:** استمرار المعدل المنخفض لـ 4 فصول متتالية أو 6 فصول متفرقة يؤدي إلى فصل الطالب."

# 4. بناء الواجهة
with gr.Blocks(title="Murshid AI | مُرشد") as demo:
    gr.Markdown(
        """
        # 🎓 مُرشد (Murshid AI)
        ### المنظومة الذكية المعتمدة للوائح كليات جامعة الريادة (حاسبات - علاج طبيعي - تمريض)
        """
    )
    
    with gr.Row():
        faculty_dropdown = gr.Dropdown(
            choices=["كلية الحاسبات والذكاء الاصطناعي", "كلية العلاج الطبيعي", "كلية التمريض"],
            value="كلية الحاسبات والذكاء الاصطناعي",
            label="🏛️ الكلية التابع لها الطالب:"
        )
    
    with gr.Tabs():
        with gr.TabItem("💬 المستشار الأكاديمي"):
            chatbot = gr.Chatbot(label="سجل المحادثة الرسمية", height=460)
            
            with gr.Accordion("🎙️ إدخال صوتي (تفريغ وتعديل النص قبل الإرسال)", open=False):
                with gr.Row():
                    audio_input = gr.Audio(sources=["microphone"], type="filepath", label="سجل استفسارك بصوتك")
                    transcribe_btn = gr.Button("تفريغ الصوت إلى نص 📝", variant="secondary")

            with gr.Row():
                text_input = gr.Textbox(
                    placeholder="اكتب استفسارك هنا أو عدل النص المفرغ ثم أرسل...",
                    label="سؤالك الأكاديمي",
                    scale=8,
                    lines=1
                )
                submit_btn = gr.Button("إرسال 🚀", variant="primary", scale=1)
                clear_btn = gr.Button("مسح السجل 🗑️", variant="stop", scale=1)

            gr.Markdown("⚡ **استفسارات سريعة بنقرة واحدة:**")
            with gr.Row():
                btn_gpa = gr.Button("📊 معدلي 1.8 كم أسجل؟")
                btn_fees = gr.Button("💰 المصروفات وشروط القبول")
                btn_pt = gr.Button("🏥 شروط وساعات سنة الامتياز")
                btn_grad = gr.Button("🎓 شروط وساعات التخرج")

        with gr.TabItem("📚 مسار المقررات والمتطلبات"):
            gr.Markdown("### 🗺️ مسار المقررات الأساسية والمتطلبات السابقة")
            gr.Dataframe(
                headers=["المقرر", "المتطلب السابق", "الكلية / المستوى"],
                value=[
                    ["برمجة متقدمة (CCS121)", "مقدمة البرمجة (CCS120)", "حاسبات - الأول ربيع"],
                    ["هياكل البيانات (CCS222)", "برمجة متقدمة (CCS121)", "حاسبات - الثاني خريف"],
                    ["تحليل وتصميم الخوارزميات (CCS223)", "برمجة متقدمة (CCS121)", "حاسبات - الثاني ربيع"],
                    ["مشروع التخرج 1 (CCS460)", "اجتياز 85 ساعة بنجاح", "حاسبات - الرابع خريف"],
                    ["تمرينات علاجية 1 (BAS108)", "تشريح 1 (BAS103)", "علاج طبيعي - الأول ربيع"],
                    ["علاج طبيعي لأمراض القلب والصدر (INT304)", "تمرينات 2 + أجهزة كهربية 2", "علاج طبيعي - الثالث خريف"],
                    ["سنة التدريب الإكلينيكي (الامتياز)", "اجتياز 197 ساعة معتمدة", "علاج طبيعي - 12 شهراً"]
                ],
                interactive=False
            )

        with gr.TabItem("⚖️ محاكي العبء الأكاديمي"):
            gr.Markdown("### 🧮 اختبار ومحاكاة الساعات المسموح بها حسب الـ CGPA")
            cgpa_slider = gr.Slider(minimum=0.0, maximum=4.0, value=1.8, step=0.05, label="المعدل التراكمي (CGPA)")
            sim_output = gr.Markdown()
            cgpa_slider.change(simulate, inputs=[cgpa_slider, faculty_dropdown], outputs=[sim_output])
            faculty_dropdown.change(simulate, inputs=[cgpa_slider, faculty_dropdown], outputs=[sim_output])
            demo.load(simulate, inputs=[cgpa_slider, faculty_dropdown], outputs=[sim_output])

    # الربط
    transcribe_btn.click(transcribe_audio, inputs=[audio_input, faculty_dropdown], outputs=[text_input])
    submit_btn.click(respond, inputs=[text_input, chatbot, faculty_dropdown], outputs=[text_input, chatbot])
    text_input.submit(respond, inputs=[text_input, chatbot, faculty_dropdown], outputs=[text_input, chatbot])
    
    # تفريغ آمن للمحادثة
    clear_btn.click(lambda: ([], "", None), outputs=[chatbot, text_input, audio_input])

    btn_gpa.click(lambda: "معدلي التراكمي 1.8، كم عدد الساعات المسموح لي بتسجيلها في الفصل الدراسي وما موقفي؟", outputs=[text_input]).then(respond, inputs=[text_input, chatbot, faculty_dropdown], outputs=[text_input, chatbot])
    btn_fees.click(lambda: "كم تبلغ المصروفات الدراسية السنوية لعام 2026/2027 وما هو الحد الأدنى للقبول؟", outputs=[text_input]).then(respond, inputs=[text_input, chatbot, faculty_dropdown], outputs=[text_input, chatbot])
    btn_pt.click(lambda: "ما هي شروط وتفاصيل ساعات تدريب سنة الامتياز الإلزامية في كلية العلاج الطبيعي ونسب الغياب؟", outputs=[text_input]).then(respond, inputs=[text_input, chatbot, faculty_dropdown], outputs=[text_input, chatbot])
    btn_grad.click(lambda: "ما هو إجمالي عدد الساعات المعتمدة المطلوبة للتخرج وشروط مشروع التخرج؟", outputs=[text_input]).then(respond, inputs=[text_input, chatbot, faculty_dropdown], outputs=[text_input, chatbot])

if __name__ == "__main__":
    demo.queue().launch(inbrowser=True, server_port=7860, show_error=True)