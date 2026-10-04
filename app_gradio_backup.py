"""
🔥 SAVAGE REPLY - AI Comeback Generator
=========================================
Built with love for a friend who needs to fight back with words.

Uses:
- Gemma 2 (open-weight LLM) via Groq for comeback generation
- edge-tts (free) for text-to-speech in English & Malayalam
- SpeechRecognition for voice input
- RAG with Malayalam movie dialogues, memes & cultural references

Run: python app.py
"""

import os
import sys
import tempfile
import time
import traceback

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

import gradio as gr

from core.comeback_engine import ComebackEngine
from core.tts_engine import TTSEngine
from core.stt_engine import STTEngine
from knowledge.knowledge_base import KnowledgeBase


# ============================================
# Initialize Components
# ============================================

def init_components():
    """Initialize all components with error handling."""
    errors = []
    
    # Knowledge Base
    try:
        kb = KnowledgeBase()
        print("✅ Knowledge base loaded")
    except Exception as e:
        kb = None
        errors.append(f"Knowledge base: {e}")
    
    # Comeback Engine
    try:
        provider = os.getenv('LLM_PROVIDER', 'groq')
        api_key = os.getenv('GROQ_API_KEY', '')
        model = os.getenv('LLM_MODEL', 'gemma2-9b-it')
        
        engine = ComebackEngine(
            provider=provider,
            api_key=api_key,
            model=model,
            knowledge_base=kb
        )
        print(f"✅ Comeback engine initialized (provider: {provider}, model: {model})")
    except Exception as e:
        engine = None
        errors.append(f"Comeback engine: {e}")
    
    # TTS Engine
    try:
        tts = TTSEngine()
        print("✅ TTS engine initialized")
    except Exception as e:
        tts = None
        errors.append(f"TTS engine: {e}")
    
    # STT Engine
    try:
        stt = STTEngine()
        print("✅ STT engine initialized")
    except Exception as e:
        stt = None
        errors.append(f"STT engine: {e}")
    
    if errors:
        print(f"\n⚠️  Some components had issues:")
        for err in errors:
            print(f"   - {err}")
    
    return engine, tts, stt, kb


# Initialize globally
engine, tts, stt, kb = init_components()


# ============================================
# Core Functions
# ============================================

def transcribe_audio(audio_path, input_language):
    """Transcribe audio recording to text."""
    if audio_path is None:
        return "🎤 No audio recorded. Please record something or type the message."
    
    if stt is None:
        return "❌ Speech recognition is not available. Please type the message instead."
    
    try:
        lang_code = 'ml' if input_language == 'Malayalam' else 'en'
        text = stt.transcribe(audio_path, language=lang_code)
        return text
    except RuntimeError as e:
        return f"⚠️ {str(e)}"
    except Exception as e:
        return f"❌ Transcription error: {str(e)}"


def generate_comebacks_handler(bully_text, output_language, num_comebacks, preferred_style):
    """Generate comebacks from the bully's text."""
    if not bully_text or not bully_text.strip():
        return "⚠️ Please enter or record what the bully said first!", []
    
    if bully_text.startswith("🎤") or bully_text.startswith("❌") or bully_text.startswith("⚠️"):
        return "⚠️ Please enter valid text or re-record the audio.", []
    
    if engine is None:
        return "❌ Comeback engine is not initialized. Check your API key in the .env file.", []
    
    try:
        # Map UI values to engine values
        lang_map = {'English': 'en', 'Malayalam': 'ml', 'Both': 'both'}
        style_map = {
            'Adaptive (Auto)': 'adaptive',
            'Savage 🔥': 'savage',
            'Funny 😂': 'funny',
            'Cool & Unbothered 🧊': 'cool_unbothered',
            'Intellectual 🧠': 'intellectual',
            'Movie Reference 🎬': 'movie_reference'
        }
        
        lang = lang_map.get(output_language, 'en')
        style = style_map.get(preferred_style, 'adaptive')
        
        comebacks = engine.generate_comebacks(
            bully_text=bully_text.strip(),
            language=lang,
            num_comebacks=int(num_comebacks),
            preferred_style=style
        )
        
        # Format comebacks as beautiful HTML cards
        html_output = format_comebacks_html(comebacks, bully_text)
        
        return html_output, comebacks
    
    except RuntimeError as e:
        return f"❌ {str(e)}", []
    except Exception as e:
        traceback.print_exc()
        return f"❌ Unexpected error: {str(e)}", []


def format_comebacks_html(comebacks, bully_text):
    """Format comebacks as beautiful HTML cards."""
    if not comebacks:
        return "<div style='text-align:center; padding:20px;'>😶 No comebacks generated. Try again!</div>"
    
    html = f"""
    <div style="font-family: 'Segoe UI', system-ui, sans-serif; max-width: 100%; padding: 10px;">
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px; padding: 15px; margin-bottom: 15px;">
            <p style="color: #8b8b8b; margin: 0 0 5px 0; font-size: 12px;">🤡 THE BULLY SAID:</p>
            <p style="color: #ff6b6b; margin: 0; font-size: 16px; font-style: italic;">"{bully_text}"</p>
        </div>
        <p style="color: #ffd93d; margin: 10px 0; font-size: 14px; text-align: center;">
            ⚡ Pick your weapon ⚡
        </p>
    """
    
    style_colors = {
        'savage': ('#ff4444', '#ff6b6b', '🔥'),
        'funny': ('#ffaa00', '#ffd93d', '😂'),
        'cool_unbothered': ('#00d2ff', '#7ee8fa', '🧊'),
        'intellectual': ('#a855f7', '#c084fc', '🧠'),
        'movie_reference': ('#22c55e', '#4ade80', '🎬'),
    }
    
    for i, comeback in enumerate(comebacks):
        style = comeback.get('style', 'savage')
        colors = style_colors.get(style, ('#ff4444', '#ff6b6b', '🔥'))
        label = comeback.get('style_label', style.replace('_', ' ').title())
        emoji = comeback.get('emoji', colors[2])
        actor = comeback.get('actor_ref', None)
        actor_badge = f'<span style="background: rgba(255,255,255,0.15); padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-left: 8px;">🎬 {actor}</span>' if actor else ''
        
        html += f"""
        <div style="background: linear-gradient(135deg, {colors[0]}22, {colors[0]}11); 
                    border-left: 4px solid {colors[0]}; border-radius: 8px; 
                    padding: 15px; margin: 10px 0; transition: transform 0.2s;"
             onmouseover="this.style.transform='scale(1.02)'" 
             onmouseout="this.style.transform='scale(1)'">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: {colors[1]}; font-weight: bold; font-size: 13px;">
                    {emoji} {label}
                </span>
                <span style="color: #666; font-size: 12px;">#{i+1}{actor_badge}</span>
            </div>
            <p style="color: #e0e0e0; margin: 0; font-size: 15px; line-height: 1.5;">
                {comeback['text']}
            </p>
        </div>
        """
    
    html += "</div>"
    return html


def speak_comeback(comebacks_state, comeback_index, tts_language, voice_gender):
    """Convert a specific comeback to speech."""
    if tts is None:
        return None
    
    if not comebacks_state or not isinstance(comebacks_state, list):
        return None
    
    try:
        idx = int(comeback_index) - 1
        if idx < 0 or idx >= len(comebacks_state):
            return None
        
        comeback_text = comebacks_state[idx]['text']
        lang = 'ml' if tts_language == 'Malayalam' else 'en'
        gender = voice_gender.lower() if voice_gender else 'male'
        
        audio_path = tts.speak_sync(
            text=comeback_text,
            language=lang,
            voice_gender=gender
        )
        
        return audio_path
    except Exception as e:
        print(f"TTS Error: {e}")
        traceback.print_exc()
        return None


# ============================================
# Gradio UI
# ============================================

def create_ui():
    """Create the Gradio interface."""
    
    # Custom CSS for mobile-first dark theme
    custom_css = """
    /* Global dark theme overrides */
    .gradio-container {
        max-width: 800px !important;
        margin: 0 auto !important;
        background: #0a0a0a !important;
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        padding: 20px 10px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        margin-bottom: 15px;
        border: 1px solid #333;
    }
    
    .app-header h1 {
        color: #ff6b35 !important;
        font-size: 2em !important;
        margin: 0 !important;
        text-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
    }
    
    .app-header p {
        color: #aaa !important;
        margin: 5px 0 0 0 !important;
    }
    
    /* Button styling */
    .generate-btn {
        background: linear-gradient(135deg, #ff6b35, #ff4444) !important;
        border: none !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        color: white !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .generate-btn:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(255, 68, 68, 0.4) !important;
    }
    
    /* Card styling */
    .comeback-card {
        border-radius: 12px !important;
        border: 1px solid #333 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 5px !important;
        }
        .app-header h1 {
            font-size: 1.5em !important;
        }
    }
    
    /* Tab styling */
    .tab-nav button {
        font-size: 1em !important;
        padding: 10px 20px !important;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        padding: 15px;
        color: #666;
        font-size: 0.85em;
    }
    """
    
    with gr.Blocks(
        title="🔥 J.O.H.A.N",
        theme=gr.themes.Soft(
            primary_hue="orange",
            secondary_hue="red",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
        css=custom_css
    ) as app:
        
        # State for storing comebacks
        comebacks_state = gr.State([])
        
        # Header
        gr.HTML("""
        <div class="app-header">
            <h1>🔥 J.O.H.A.N</h1>
            <p>Your AI-Powered Comeback Generator</p>
            <p style="font-size: 0.8em; color: #666; margin-top: 8px;">
                Powered by Gemma 2 (Open-Weight) • Malayalam & English • Built for a friend ❤️
            </p>
        </div>
        """)
        
        # Input Section
        with gr.Group():
            gr.Markdown("### 🎯 What did the bully say?")
            
            with gr.Tabs() as input_tabs:
                # Text Input Tab
                with gr.Tab("✍️ Type It", id="text_tab"):
                    bully_text = gr.Textbox(
                        placeholder="Type what the bully said here...",
                        lines=3,
                        label="Bully's Message",
                        show_label=False
                    )
                
                # Voice Input Tab
                with gr.Tab("🎤 Record It", id="voice_tab"):
                    input_language = gr.Radio(
                        choices=["English", "Malayalam"],
                        value="English",
                        label="They spoke in:",
                        interactive=True
                    )
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Record what they said",
                    )
                    transcribe_btn = gr.Button(
                        "📝 Transcribe",
                        variant="secondary",
                        size="sm"
                    )
                    transcribed_text = gr.Textbox(
                        label="Transcribed Text (edit if needed)",
                        placeholder="Click 'Transcribe' after recording...",
                        lines=2,
                        interactive=True
                    )
        
        # Settings Row
        with gr.Group():
            with gr.Row():
                output_language = gr.Dropdown(
                    choices=["English", "Malayalam", "Both"],
                    value="English",
                    label="🌐 Reply Language",
                    interactive=True
                )
                num_comebacks = gr.Slider(
                    minimum=3,
                    maximum=7,
                    value=5,
                    step=1,
                    label="🔢 How many comebacks?",
                    interactive=True
                )
            
            preferred_style = gr.Radio(
                choices=[
                    "Adaptive (Auto)",
                    "Savage 🔥",
                    "Funny 😂",
                    "Cool & Unbothered 🧊",
                    "Intellectual 🧠",
                    "Movie Reference 🎬"
                ],
                value="Adaptive (Auto)",
                label="🎭 Comeback Style",
                interactive=True
            )
        
        # Generate Button
        generate_btn = gr.Button(
            "⚡ GENERATE COMEBACKS ⚡",
            variant="primary",
            elem_classes="generate-btn",
            size="lg"
        )
        
        # Results Section
        gr.Markdown("### 💬 Your Comebacks")
        comebacks_html = gr.HTML(
            value="<div style='text-align:center; padding:40px; color:#666;'>Your comebacks will appear here... 🎯</div>"
        )
        
        # TTS Section
        with gr.Group():
            gr.Markdown("### 🔊 Hear It Out Loud")
            with gr.Row():
                comeback_index = gr.Dropdown(
                    choices=["1", "2", "3", "4", "5", "6", "7"],
                    value="1",
                    label="Which comeback? (#)",
                    interactive=True
                )
                tts_language = gr.Dropdown(
                    choices=["English", "Malayalam"],
                    value="English",
                    label="Read in:",
                    interactive=True
                )
                voice_gender = gr.Radio(
                    choices=["Male", "Female"],
                    value="Male",
                    label="Voice:",
                    interactive=True
                )
            
            speak_btn = gr.Button(
                "🔊 Read This Comeback",
                variant="secondary"
            )
            audio_output = gr.Audio(
                label="🔊 Listen",
                type="filepath",
                interactive=False
            )
        
        # Footer
        gr.HTML("""
        <div class="app-footer">
            <p>🔥 Built with ❤️ using open-source AI</p>
            <p>Gemma 2 (Open-Weight) • edge-tts • Gradio</p>
            <p style="margin-top: 5px; font-size: 0.8em;">
                🛡️ No relative/family jokes • Your data stays private
            </p>
        </div>
        """)
        
        # ============================================
        # Event Handlers
        # ============================================
        
        # Transcribe audio
        transcribe_btn.click(
            fn=transcribe_audio,
            inputs=[audio_input, input_language],
            outputs=[transcribed_text]
        )
        
        # Generate comebacks - smart handler that uses typed text or transcribed text
        def smart_generate(typed_text, transcribed, out_lang, n_comebacks, style):
            """Use typed text if available, otherwise use transcribed text."""
            text = typed_text.strip() if typed_text and typed_text.strip() else transcribed
            if not text or not text.strip():
                return "⚠️ Please type or record what the bully said first!", []
            html, comebacks = generate_comebacks_handler(text, out_lang, n_comebacks, style)
            return html, comebacks
        
        # Override the generate button to be smart about input source
        generate_btn.click(
            fn=smart_generate,
            inputs=[bully_text, transcribed_text, output_language, num_comebacks, preferred_style],
            outputs=[comebacks_html, comebacks_state]
        )
        
        # Speak comeback
        speak_btn.click(
            fn=speak_comeback,
            inputs=[comebacks_state, comeback_index, tts_language, voice_gender],
            outputs=[audio_output]
        )
    
    return app


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    print("")
    print("🔥 ============================================")
    print("   J.O.H.A.N - AI Comeback Generator")
    print("🔥 ============================================")
    print("")
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY', '')
    if not api_key or api_key == 'your_groq_api_key_here':
        print("⚠️  WARNING: No Groq API key found!")
        print("   Get a FREE key at: https://console.groq.com")
        print("   Then set it in your .env file")
        print("")
    
    # Determine share setting
    share = os.getenv('GRADIO_SHARE', 'true').lower() == 'true'
    
    app = create_ui()
    
    print("🚀 Starting server...")
    print(f"   Share mode: {'ON (public URL for phone access)' if share else 'OFF (local only)'}")
    print("")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share,
        show_error=True,
        favicon_path=None
    )
