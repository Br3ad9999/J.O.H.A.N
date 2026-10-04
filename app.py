import os
import sys
import tempfile
import time
import traceback
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from core.comeback_engine import ComebackEngine
from core.tts_engine import TTSEngine
from core.stt_engine import STTEngine
from knowledge.knowledge_base import KnowledgeBase

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(PROJECT_ROOT, 'audio_cache')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================
# Initialize Components
# ============================================
def init_components():
    """Initialize all components with error handling."""
    errors = []
    
    # Knowledge Base
    try:
        kb = KnowledgeBase()
        print("Knowledge base loaded")
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
        print(f"Comeback engine initialized (provider: {provider}, model: {model})")
    except Exception as e:
        engine = None
        errors.append(f"Comeback engine: {e}")
    
    # TTS Engine
    try:
        tts = TTSEngine()
        print("TTS engine initialized")
    except Exception as e:
        tts = None
        errors.append(f"TTS engine: {e}")
    
    # STT Engine
    try:
        stt = STTEngine()
        print("STT engine initialized")
    except Exception as e:
        stt = None
        errors.append(f"STT engine: {e}")
    
    if errors:
        print(f"\nSome components had issues:")
        for err in errors:
            print(f"   - {err}")
    
    return engine, tts, stt, kb

engine, tts, stt, kb = init_components()

# ============================================
# Routes
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    input_language = request.form.get('input_language', 'English')
    
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if stt is None:
        return jsonify({'error': 'Speech recognition is not available'}), 503
        
    try:
        filename = secure_filename("upload_" + str(int(time.time())) + ".webm")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        lang_code = 'ml' if input_language == 'Malayalam' else 'en'
        text = stt.transcribe(filepath, language=lang_code)
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify({'text': text})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    bully_text = data.get('bully_text', '')
    output_language = data.get('output_language', 'English')
    num_comebacks = int(data.get('num_comebacks', 5))
    preferred_style = data.get('preferred_style', 'Adaptive (Auto)')
    
    if not bully_text or not bully_text.strip():
        return jsonify({'error': 'Please enter what the bully said'}), 400
        
    if engine is None:
        return jsonify({'error': 'Comeback engine is not initialized'}), 503
        
    try:
        lang_map = {'English': 'en', 'Malayalam': 'ml'}
        style_map = {
            'Adaptive (Auto)': 'adaptive',
            'Savage': 'savage',
            'Funny': 'funny',
            'Cool & Unbothered': 'cool_unbothered',
            'Intellectual': 'intellectual',
            'Movie Reference': 'movie_reference'
        }
        
        lang = lang_map.get(output_language, 'en')
        style = style_map.get(preferred_style, 'adaptive')
        
        comebacks = engine.generate_comebacks(
            bully_text=bully_text.strip(),
            language=lang,
            num_comebacks=num_comebacks,
            preferred_style=style
        )
        
        return jsonify({'comebacks': comebacks})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    tts_language = data.get('tts_language', 'English')
    voice_gender = data.get('voice_gender', 'Male')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
        
    if tts is None:
        return jsonify({'error': 'TTS engine is not available'}), 503
        
    try:
        lang = 'ml' if tts_language == 'Malayalam' else 'en'
        gender = voice_gender.lower() if voice_gender else 'male'
        
        audio_path = tts.speak_sync(
            text=text,
            language=lang,
            voice_gender=gender
        )
        
        # We need to return the URL to the audio file
        filename = os.path.basename(audio_path)
        return jsonify({'audio_url': f'/audio/{filename}'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    audio_dir = os.path.join(PROJECT_ROOT, 'audio_cache')
    return send_file(os.path.join(audio_dir, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
