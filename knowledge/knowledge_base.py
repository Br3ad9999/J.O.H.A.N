import json
import os
import random
from pathlib import Path

class KnowledgeBase:
    def __init__(self, knowledge_dir: str = None):
        if knowledge_dir is None:
            knowledge_dir = os.path.dirname(os.path.abspath(__file__))
        self.knowledge_dir = Path(knowledge_dir)
        self._load_all()
    
    def _load_all(self):
        # Load all JSON files
        self.dialogues = self._load_json('malayalam_dialogues.json')['dialogues']
        self.templates = self._load_json('comeback_templates.json')
        self.memes = self._load_json('meme_references.json')['memes']
        self.actors = self._load_json('actor_styles.json')['actors']
    
    def _load_json(self, filename):
        filepath = self.knowledge_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_relevant_context(self, bully_text: str, language: str = 'en', num_items: int = 5) -> str:
        """Build a context string with relevant knowledge for the LLM."""
        # Get random dialogues for inspiration
        dialogues = self.get_random_dialogues(n=num_items)
        # Get random memes
        memes = self.get_random_memes(n=3)
        # Get style info based on detected severity
        style_info = self.templates.get('styles', {})
        
        context_parts = []
        context_parts.append("=== MALAYALAM MOVIE DIALOGUES FOR INSPIRATION ===")
        for d in dialogues:
            context_parts.append(f"- [{d['actor']} in {d['movie']}]: \"{d['text_ml']}\" ({d['text_en']}) - Mood: {d['mood']}")
        
        context_parts.append("\n=== MEME REFERENCES ===")
        for m in memes:
            context_parts.append(f"- {m['name']}: {m['format']} (Example comeback: {m['example_comeback']})")
        
        context_parts.append("\n=== ACTOR STYLES ===")
        for actor in random.sample(self.actors, min(3, len(self.actors))):
            context_parts.append(f"- {actor['name']} ({actor['nickname']}): {actor['style_description']}")
        
        return "\n".join(context_parts)
    
    def get_random_dialogues(self, actor: str = None, n: int = 5) -> list:
        pool = self.dialogues
        if actor:
            pool = [d for d in self.dialogues if d['actor'].lower() == actor.lower()]
        return random.sample(pool, min(n, len(pool)))
    
    def get_random_memes(self, n: int = 3) -> list:
        return random.sample(self.memes, min(n, len(self.memes)))
    
    def get_actor_style(self, actor_name: str) -> dict:
        for actor in self.actors:
            if actor['name'].lower() == actor_name.lower() or actor.get('nickname', '').lower() == actor_name.lower():
                return actor
        return None
    
    def get_all_actors(self) -> list:
        return [a['name'] for a in self.actors]
    
    def get_style_info(self, style: str) -> dict:
        return self.templates.get('styles', {}).get(style, {})
    
    def get_adaptive_rules(self) -> list:
        return self.templates.get('adaptive_rules', [])
