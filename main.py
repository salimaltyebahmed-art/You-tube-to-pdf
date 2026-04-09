import yt_dlp
import whisper
import google.generativeai as genai
import os
from IPython.display import Markdown, display
import markdown
from weasyprint import HTML

# ==========================================
# 1. الإعدادات
# ==========================================
GOOGLE_API_KEY = "............" 
genai.configure(api_key=GOOGLE_API_KEY)

def process_video_agent3_style(video_url):
    print(f"🚀 1. Harvesting: جارٍ سحب الفيديو...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],
        'outtmpl': 'temp_audio.%(ext)s',
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        title = info.get('title', 'Video')

    # -------------------------------------------
    print("🎧 2. Transcribing: جارٍ النسخ الدقيق...")
    model = whisper.load_model("medium", device="cuda")
    result = model.transcribe("temp_audio.mp3")
    transcript = result["text"]
    
    # -------------------------------------------
    print("🧠 3. Synthesizing: تشغيل محاكاة Agent 3 (The Brain)...")
    
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
    
    # هنا قمنا بتحويل كود البايثون المعقد إلى تعليمات لـ Gemini
    agent3_prompt = f"""
    ROLE: You are "Agent 3: Knowledge Synthesizer". 
    Your code logic is based on: Semantic Deduplication, Conflict Resolution, and Visual Context Extraction.

    INPUT DATA:
    - Title: {title}
    - Transcript: {transcript[:100000]}

    TASK: transform this transcript into a structured Academic PDF Content.

    --- EXECUTION RULES (Based on Python Logic) ---

    1. [VisualContextExtractor]:
       Scan the text for trigger phrases like "as you can see", "look at this", "shown here", "diagram", "circuit".
       Where found, insert a tag: [[SCREENSHOT: Describe exactly what is shown | Timestamp approx]]
       *DO NOT* invent screenshots if the speaker doesn't point to something.

    2. [ConflictResolver]:
       If the speaker contradicts themselves or clarifies a common misconception (e.g., "People say X, but actually Y"), 
       create a "⚠️ WARNING BOX" explaining the conflict.

    3. [ConceptMapper]:
       Organize the content logically (DAG structure): 
       Definition -> Concept -> Example -> Application.
       Do not just summarize chronologically; reorder for teaching.

    4. [SemanticDeduplicator]:
       If the speaker repeats the same concept multiple times, merge them into one clear section. Do not repeat text.

    --- OUTPUT FORMAT (Markdown) ---

    # {title}

    ## 📌 Core Concepts Map
    (List the 3-5 main concepts defined in the video)

    ## 📘 Detailed Knowledge
    (The main content, reordered for learning, with equations in LaTeX $$x$$)

    > **Visual Notes:**
    > (Place [[SCREENSHOT...]] tags here inside the relevant sections)

    ## ⚠️ Critical Conflicts & Warnings
    (Any safety warnings or corrected misconceptions)
    """
    
    try:
        response = gemini_model.generate_content(agent3_prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {e}"

# ==========================================
# التشغيل
# ==========================================
url = "https://youtube.com/..."

final_md = process_video_agent3_style(url)

display(Markdown(final_md))
html = markdown.markdown(final_md)
HTML(string=html).write_pdf("Agent3_Output.pdf")
print("✅ تم استخراج المعرفة بمنطق Agent 3!")
