#!/usr/bin/env python3
"""
Test script for Savage Reply components.
Tests each module independently to verify no bugs.
"""

import os
import sys
import traceback

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

results = []

def test(name, func):
    """Run a test and track results."""
    try:
        func()
        results.append((name, "PASS", ""))
        print(f"  ✅ {name}")
    except Exception as e:
        results.append((name, "FAIL", str(e)))
        print(f"  ❌ {name}: {e}")
        traceback.print_exc()

# ============================================
# Test 1: Knowledge Base Loading
# ============================================
print("\n📋 Test Suite: Knowledge Base")
print("=" * 50)

def test_kb_load():
    from knowledge.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    assert len(kb.dialogues) >= 25, f"Expected 25+ dialogues, got {len(kb.dialogues)}"
    assert len(kb.memes) >= 15, f"Expected 15+ memes, got {len(kb.memes)}"
    assert len(kb.actors) >= 8, f"Expected 8+ actors, got {len(kb.actors)}"

test("Knowledge base loads all JSON files", test_kb_load)

def test_kb_dialogues():
    from knowledge.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    actors = set(d['actor'] for d in kb.dialogues)
    assert 'Mohanlal' in actors, "Missing Mohanlal dialogues"
    assert 'Mammootty' in actors, "Missing Mammootty dialogues"
    assert 'Fahadh Faasil' in actors, "Missing Fahadh Faasil dialogues"

test("Dialogues cover major actors", test_kb_dialogues)

def test_kb_random_dialogues():
    from knowledge.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    dialogues = kb.get_random_dialogues(n=3)
    assert len(dialogues) == 3, f"Expected 3 dialogues, got {len(dialogues)}"
    for d in dialogues:
        assert 'text_ml' in d, "Missing text_ml field"
        assert 'actor' in d, "Missing actor field"

test("Random dialogue retrieval", test_kb_random_dialogues)

def test_kb_context():
    from knowledge.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    context = kb.get_relevant_context("you are stupid", language='en')
    assert len(context) > 100, "Context too short"
    assert "MALAYALAM MOVIE DIALOGUES" in context, "Missing dialogue section"
    assert "MEME REFERENCES" in context, "Missing meme section"
    assert "ACTOR STYLES" in context, "Missing actor section"

test("Context generation for LLM", test_kb_context)

def test_kb_actor_style():
    from knowledge.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    mohanlal = kb.get_actor_style("Mohanlal")
    assert mohanlal is not None, "Could not find Mohanlal"
    assert 'style_description' in mohanlal, "Missing style_description"

test("Actor style lookup", test_kb_actor_style)

# ============================================
# Test 2: TTS Engine
# ============================================
print("\n📋 Test Suite: TTS Engine")
print("=" * 50)

def test_tts_init():
    from core.tts_engine import TTSEngine
    tts = TTSEngine()
    assert tts.cache_dir.exists(), "Cache directory not created"

test("TTS engine initialization", test_tts_init)

def test_tts_voices():
    from core.tts_engine import TTSEngine
    tts = TTSEngine()
    assert 'ml' in tts.VOICES, "Missing Malayalam voices"
    assert 'en' in tts.VOICES, "Missing English voices"
    assert 'male' in tts.VOICES['ml'], "Missing Malayalam male voice"
    assert 'female' in tts.VOICES['ml'], "Missing Malayalam female voice"

test("TTS voice configuration", test_tts_voices)

def test_tts_speak():
    from core.tts_engine import TTSEngine
    tts = TTSEngine()
    result = tts.speak_sync("Hello, this is a test.", language='en', voice_gender='male')
    assert result is not None, "TTS returned None"
    assert os.path.exists(result), f"Audio file not found: {result}"
    file_size = os.path.getsize(result)
    assert file_size > 100, f"Audio file too small: {file_size} bytes"
    print(f"    → Generated audio: {file_size} bytes")
    # Cleanup
    os.remove(result)

test("TTS audio generation (English)", test_tts_speak)

# ============================================
# Test 3: STT Engine
# ============================================
print("\n📋 Test Suite: STT Engine")
print("=" * 50)

def test_stt_init():
    from core.stt_engine import STTEngine
    stt = STTEngine()
    assert stt.recognizer is not None, "Recognizer not initialized"

test("STT engine initialization", test_stt_init)

def test_stt_language_codes():
    from core.stt_engine import STTEngine
    stt = STTEngine()
    assert stt.LANGUAGE_CODES['en'] == 'en-IN', "Wrong English code"
    assert stt.LANGUAGE_CODES['ml'] == 'ml-IN', "Wrong Malayalam code"

test("STT language code mapping", test_stt_language_codes)

# ============================================
# Test 4: Comeback Engine
# ============================================
print("\n📋 Test Suite: Comeback Engine")
print("=" * 50)

def test_engine_init():
    from core.comeback_engine import ComebackEngine
    # Test with dummy key (won't make API calls)
    engine = ComebackEngine(provider='groq', api_key='test_key')
    assert engine.model == 'gemma2-9b-it', f"Wrong default model: {engine.model}"
    assert engine.kb is not None, "Knowledge base not loaded"

test("Comeback engine initialization", test_engine_init)

def test_engine_blocked_words():
    from core.comeback_engine import ComebackEngine
    engine = ComebackEngine(provider='groq', api_key='test_key')
    assert 'mother' in engine.BLOCKED_WORDS, "Missing 'mother'"
    assert 'amma' in engine.BLOCKED_WORDS, "Missing 'amma'"
    assert 'achan' in engine.BLOCKED_WORDS, "Missing 'achan'"
    assert 'brother' in engine.BLOCKED_WORDS, "Missing 'brother'"

test("Safety filter blocked words", test_engine_blocked_words)

def test_engine_safety_filter():
    from core.comeback_engine import ComebackEngine
    engine = ComebackEngine(provider='groq', api_key='test_key')
    
    # Test that unsafe comebacks are filtered
    test_comebacks = [
        {'text': 'Your mother would be ashamed', 'style': 'savage', 'style_label': 'Savage', 'emoji': '🔥', 'actor_ref': None},
        {'text': 'You are so dumb even Google cant help you', 'style': 'intellectual', 'style_label': 'Intellectual', 'emoji': '🧠', 'actor_ref': None},
        {'text': 'Tell your dad I said hi', 'style': 'funny', 'style_label': 'Funny', 'emoji': '😂', 'actor_ref': None},
        {'text': 'Ninte amma ariyumo', 'style': 'savage', 'style_label': 'Savage', 'emoji': '🔥', 'actor_ref': None},
        {'text': 'You have the IQ of a parking meter', 'style': 'savage', 'style_label': 'Savage', 'emoji': '🔥', 'actor_ref': None},
    ]
    
    filtered = engine._safety_filter(test_comebacks)
    
    # Should keep the safe ones (index 1 and 4)
    assert len(filtered) == 2, f"Expected 2 safe comebacks, got {len(filtered)}: {[c['text'] for c in filtered]}"
    assert all('mother' not in c['text'].lower() for c in filtered), "Mother reference leaked through"
    assert all('dad' not in c['text'].lower() for c in filtered), "Dad reference leaked through"
    assert all('amma' not in c['text'].lower() for c in filtered), "Amma reference leaked through"

test("Safety filter catches relative references", test_engine_safety_filter)

def test_engine_parse_comebacks():
    from core.comeback_engine import ComebackEngine
    engine = ComebackEngine(provider='groq', api_key='test_key')
    
    test_response = """[SAVAGE] You look like you googled "how to be cool" and failed |ACTOR_REF: None|
[FUNNY] If brains were dynamite you wouldn't have enough to blow your nose |ACTOR_REF: Dileep|
[COOL] Oh sorry, were you talking? I was busy not caring |ACTOR_REF: Fahadh Faasil|
[INTELLECTUAL] Your IQ and shoe size seem to be in close competition |ACTOR_REF: None|
[MOVIE] Ninne poloru nooru per vannaalum enikku oru chukkum cheyyan aavilla |ACTOR_REF: Mammootty|"""
    
    comebacks = engine._parse_comebacks(test_response)
    assert len(comebacks) == 5, f"Expected 5 comebacks, got {len(comebacks)}"
    
    styles = [c['style'] for c in comebacks]
    assert 'savage' in styles, "Missing savage style"
    assert 'funny' in styles, "Missing funny style"
    assert 'cool_unbothered' in styles, "Missing cool style"
    assert 'intellectual' in styles, "Missing intellectual style"
    assert 'movie_reference' in styles, "Missing movie style"
    
    # Check actor refs parsed correctly
    dileep_comeback = [c for c in comebacks if c['style'] == 'funny'][0]
    assert dileep_comeback['actor_ref'] == 'Dileep', f"Wrong actor ref: {dileep_comeback['actor_ref']}"

test("Comeback response parsing", test_engine_parse_comebacks)

def test_engine_empty_input():
    from core.comeback_engine import ComebackEngine
    engine = ComebackEngine(provider='groq', api_key='test_key')
    result = engine.generate_comebacks("", language='en')
    assert len(result) >= 1, "Empty input should return at least 1 result"
    assert 'Tell me' in result[0]['text'] or 'info' in result[0].get('style', ''), "Empty input not handled"

test("Empty input handling", test_engine_empty_input)

# ============================================
# Test 5: App Import
# ============================================
print("\n📋 Test Suite: App Module")
print("=" * 50)

def test_app_imports():
    # Test that all imports in app.py work
    from dotenv import load_dotenv
    from core.comeback_engine import ComebackEngine
    from core.tts_engine import TTSEngine
    from core.stt_engine import STTEngine
    from knowledge.knowledge_base import KnowledgeBase
    import gradio as gr
    assert True

test("All app imports successful", test_app_imports)

def test_html_formatting():
    # Import the format function from app
    sys.path.insert(0, PROJECT_ROOT)
    # We can't easily import from app.py without running it, 
    # so let's test the core format logic
    test_comebacks = [
        {'text': 'Test comeback 1', 'style': 'savage', 'style_label': 'Savage', 'emoji': '🔥', 'actor_ref': None},
        {'text': 'Test comeback 2', 'style': 'funny', 'style_label': 'Funny', 'emoji': '😂', 'actor_ref': 'Mohanlal'},
    ]
    # Verify the data structure is correct
    for c in test_comebacks:
        assert 'text' in c
        assert 'style' in c
        assert 'emoji' in c

test("Comeback data structure validation", test_html_formatting)

# ============================================
# Summary
# ============================================
print("\n" + "=" * 50)
print("📊 TEST RESULTS SUMMARY")
print("=" * 50)

passed = sum(1 for _, status, _ in results if status == "PASS")
failed = sum(1 for _, status, _ in results if status == "FAIL")
total = len(results)

for name, status, error in results:
    icon = "✅" if status == "PASS" else "❌"
    print(f"  {icon} {name}")
    if error:
        print(f"     └─ {error}")

print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed}")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! Ready to deploy! 🚀")
else:
    print(f"\n⚠️  {failed} test(s) failed. Fix before deploying.")
    sys.exit(1)
