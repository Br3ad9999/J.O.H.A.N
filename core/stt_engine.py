import speech_recognition as sr
import os
import tempfile
from pathlib import Path

class STTEngine:
    LANGUAGE_CODES = {
        'en': 'en-IN',
        'ml': 'ml-IN',
        'english': 'en-IN',
        'malayalam': 'ml-IN'
    }
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
    
    def transcribe(self, audio_file_path: str, language: str = 'en') -> str:
        """Transcribe an audio file to text.
        
        Args:
            audio_file_path: Path to the audio file (WAV, FLAC, MP3, etc.)
            language: Language code ('en', 'ml', 'english', 'malayalam')
        
        Returns:
            Transcribed text string
        
        Raises:
            ValueError: If audio file not found or unreadable
            RuntimeError: If transcription fails
        """
        if not os.path.exists(audio_file_path):
            raise ValueError(f"Audio file not found: {audio_file_path}")
        
        lang_code = self.LANGUAGE_CODES.get(language.lower(), 'en-IN')
        
        try:
            # Convert to WAV if needed using pydub
            wav_path = self._ensure_wav(audio_file_path)
            
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Use Google's free speech recognition
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            # Clean up temp WAV if we created one
            if wav_path != audio_file_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            return text.strip()
            
        except sr.UnknownValueError:
            raise RuntimeError("Could not understand the audio. Please speak clearly and try again.")
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}. Check your internet connection.")
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def _ensure_wav(self, audio_path: str) -> str:
        """Convert audio file to WAV format if it isn't already."""
        if audio_path.lower().endswith('.wav'):
            return audio_path
        
        try:
            from pydub import AudioSegment
            
            # Detect format from extension
            ext = Path(audio_path).suffix.lower().lstrip('.')
            if ext in ('mp3', 'ogg', 'flac', 'webm', 'm4a', 'aac'):
                audio = AudioSegment.from_file(audio_path, format=ext)
            else:
                audio = AudioSegment.from_file(audio_path)
            
            # Export as WAV
            wav_path = tempfile.mktemp(suffix='.wav')
            audio.export(wav_path, format='wav')
            return wav_path
            
        except ImportError:
            raise RuntimeError("pydub is required for non-WAV audio files. Install it: pip install pydub")
        except Exception as e:
            raise RuntimeError(f"Could not convert audio file: {str(e)}")
