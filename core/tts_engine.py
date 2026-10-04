import edge_tts
import asyncio
import os
import tempfile
import uuid
from pathlib import Path

class TTSEngine:
    # Malayalam voices
    VOICES = {
        'ml': {
            'male': 'ml-IN-MidhunNeural',
            'female': 'ml-IN-SobhanaNeural'
        },
        'en': {
            'male': 'en-IN-PrabhatNeural',
            'female': 'en-IN-NeerjaNeural'
        }
    }
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio_cache')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def speak(self, text: str, language: str = 'en', voice_gender: str = 'male') -> str:
        """Convert text to speech. Returns path to audio file."""
        try:
            lang_key = 'ml' if language.startswith('ml') else 'en'
            voice = self.VOICES[lang_key][voice_gender]
            
            output_file = str(self.cache_dir / f"{uuid.uuid4().hex}.mp3")
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            
            return output_file
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def speak_sync(self, text: str, language: str = 'en', voice_gender: str = 'male') -> str:
        """Synchronous wrapper for speak()."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is already running (e.g., in Gradio), create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(self._run_in_new_loop, text, language, voice_gender).result()
                return result
            else:
                return loop.run_until_complete(self.speak(text, language, voice_gender))
        except RuntimeError:
            return self._run_in_new_loop(text, language, voice_gender)
    
    def _run_in_new_loop(self, text: str, language: str, voice_gender: str) -> str:
        """Run TTS in a new event loop (for use within async contexts)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.speak(text, language, voice_gender))
        finally:
            loop.close()
    
    def cleanup_cache(self, max_files: int = 50):
        """Remove old cached audio files."""
        files = sorted(self.cache_dir.glob('*.mp3'), key=os.path.getmtime)
        while len(files) > max_files:
            files[0].unlink()
            files.pop(0)
