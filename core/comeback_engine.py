import os
import json
import re
from typing import Optional

# Add parent directory to path for knowledge base import
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knowledge.knowledge_base import KnowledgeBase


class ComebackEngine:
    """Core engine for generating witty comebacks using open-weight LLMs."""
    
    # Words/topics that are OFF-LIMITS (relative references)
    BLOCKED_WORDS = [
        'mother', 'father', 'mom', 'dad', 'sister', 'brother', 'parent',
        'amma', 'achan', 'chechi', 'chettan', 'chetta', 'appan', 'amma',
        'wife', 'husband', 'family', 'kudumbam', 'relative',
        'grandmother', 'grandfather', 'ammamma', 'appappan', 'muthassi',
        'uncle', 'aunt', 'maman', 'ammavan', 'ammayi',
        'son', 'daughter', 'makan', 'makal', 'mon', 'mol',
        # Malayalam variants
        'thantha', 'maatha', 'sahotharan', 'sahothary'
    ]
    
    STYLE_CONFIGS = {
        'savage': {'emoji': '', 'label': 'Savage'},
        'funny': {'emoji': '', 'label': 'Funny'},
        'cool_unbothered': {'emoji': '', 'label': 'Cool & Unbothered'},
        'intellectual': {'emoji': '', 'label': 'Intellectual'},
        'movie_reference': {'emoji': '', 'label': 'Movie Reference'}
    }
    
    def __init__(self, provider: str = 'groq', api_key: str = None, model: str = None, knowledge_base: KnowledgeBase = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv('GROQ_API_KEY', '')
        
        # Set default model based on provider
        if model:
            self.model = model
        elif self.provider == 'groq':
            self.model = 'gemma2-9b-it'
        elif self.provider == 'ollama':
            self.model = 'gemma2:2b'  # Small enough for low-RAM systems
        else:
            self.model = 'gemma2-9b-it'
        
        # Initialize knowledge base
        if knowledge_base:
            self.kb = knowledge_base
        else:
            kb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'knowledge')
            self.kb = KnowledgeBase(kb_dir)
        
        # Initialize LLM client
        self._init_client()
    
    def _init_client(self):
        """Initialize the LLM client based on provider."""
        if self.provider == 'groq':
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("groq package required. Install: pip install groq")
        elif self.provider == 'ollama':
            try:
                import ollama
                self.client = ollama
            except ImportError:
                raise ImportError("ollama package required. Install: pip install ollama")
    
    def generate_comebacks(self, bully_text: str, language: str = 'en', num_comebacks: int = 5, preferred_style: str = 'adaptive') -> list:
        """
        Generate witty comebacks for the given bully's text.
        
        Args:
            bully_text: What the bully said
            language: 'en' for English, 'ml' for Malayalam, 'both' for both
            num_comebacks: Number of comebacks to generate
            preferred_style: 'adaptive' (auto-detect), or a specific style name
        
        Returns:
            List of dicts: [{'text': str, 'style': str, 'emoji': str, 'actor_ref': str|None}]
        """
        if not bully_text.strip():
            return [{'text': 'Tell me what they said first!', 'style': 'info', 'emoji': '', 'actor_ref': None}]
        
        # Get relevant knowledge context
        knowledge_context = self.kb.get_relevant_context(bully_text, language)
        
        # Build the prompt
        prompt = self._build_prompt(bully_text, language, knowledge_context, num_comebacks, preferred_style)
        
        # Call LLM
        raw_response = self._call_llm(prompt)
        
        # Parse comebacks
        comebacks = self._parse_comebacks(raw_response)
        
        # Safety filter - remove any that mention relatives
        comebacks = self._safety_filter(comebacks)
        
        # If filtering removed too many, regenerate
        if len(comebacks) < 2:
            # Try once more with stronger instructions
            prompt = self._build_prompt(bully_text, language, knowledge_context, num_comebacks, preferred_style, extra_strict=True)
            raw_response = self._call_llm(prompt)
            comebacks = self._parse_comebacks(raw_response)
            comebacks = self._safety_filter(comebacks)
        
        return comebacks[:num_comebacks] if comebacks else [{'text': 'Even my AI is speechless at how lame that insult was', 'style': 'cool_unbothered', 'emoji': '', 'actor_ref': None}]
    
    def _build_prompt(self, bully_text: str, language: str, knowledge_context: str, num_comebacks: int, preferred_style: str, extra_strict: bool = False) -> str:
        """Build the system + user prompt for comeback generation."""
        
        language_instruction = {
            'en': 'Generate all comebacks in ENGLISH.',
            'ml': 'CRITICAL: You MUST write the comeback text entirely in NATIVE MALAYALAM SCRIPT (മലയാളം അക്ഷരമാല). DO NOT use English script or Manglish!'
        }.get(language, 'Generate all comebacks in ENGLISH.')
        
        style_instruction = ''
        if preferred_style == 'adaptive':
            style_instruction = '''Analyze the severity of the bully's message and adapt:
- If it's MILD teasing → Use more Funny and Cool/Unbothered comebacks
- If it's MODERATE meanness → Mix Savage, Movie Reference, and Intellectual comebacks  
- If it's HARSH personal attack → Lead with Savage and Intellectual, show dominance without stooping to their level'''
        else:
            style_instruction = f'Focus on the "{preferred_style}" style for all comebacks.'
        
        strict_warning = ''
        if extra_strict:
            strict_warning = '\n\nCRITICAL: You MUST NOT mention any family members, relatives, parents, siblings, etc. in ANY comeback. This is a HARD RULE. Violating this will cause the response to be rejected.'
        
        system_prompt = f"""You are SAVAGE REPLY, an AI that generates witty, clever, and devastating comebacks. You are deeply versed in Malayalam cinema, memes, and pop culture.

Your comebacks should be:
1. CLEVER - Not just mean, but genuinely witty
2. CULTURALLY RICH - Reference Malayalam movies, actors, memes when appropriate
3. PROPORTIONAL - Match the energy of the original insult
4. CLEAN OF FAMILY REFERENCES - NEVER mention anyone's mother, father, parents, siblings, family, relatives, wife, husband, children. This is an ABSOLUTE rule. NO exceptions.
5. NON-VIOLENT - No threats of physical harm
6. FUNNY - Even savage comebacks should make people laugh

{language_instruction}

{style_instruction}
{strict_warning}

Here's some cultural knowledge to draw from:

{knowledge_context}

IMPORTANT: For each comeback, you MUST use EXACTLY this format:
[STYLE_TAG] comeback text here |ACTOR_REF: actor name or None|

Valid STYLE_TAGs: [SAVAGE], [FUNNY], [COOL], [INTELLECTUAL], [MOVIE]

NO INTRODUCTORY TEXT. NO CHATTY FILLER. OUTPUT ONLY THE COMEBACKS.
Generate exactly {num_comebacks} comebacks, each on a new line."""
        
        user_prompt = f"""The bully said: \"{bully_text}\"

Generate {num_comebacks} killer comebacks. Remember: NO family/relative references whatsoever."""
        
        if language == 'ml':
            user_prompt += "\nCRITICAL: Output ONLY in native Malayalam script (മലയാളം). NO English!"
            
        return json.dumps({'system': system_prompt, 'user': user_prompt})
    
    def _call_llm(self, prompt_json: str) -> str:
        """Call the LLM provider."""
        prompts = json.loads(prompt_json)
        
        try:
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {'role': 'system', 'content': prompts['system']},
                        {'role': 'user', 'content': prompts['user']}
                    ],
                    temperature=0.9,
                    max_tokens=1500,
                    top_p=0.95
                )
                return response.choices[0].message.content
            
            elif self.provider == 'ollama':
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {'role': 'system', 'content': prompts['system']},
                        {'role': 'user', 'content': prompts['user']}
                    ],
                    options={'temperature': 0.9, 'num_predict': 1500}
                )
                return response['message']['content']
            
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
                
        except Exception as e:
            error_msg = str(e)
            if 'api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
                raise RuntimeError(f"API key error. Please set your GROQ_API_KEY in the .env file. Get a free key at https://console.groq.com")
            raise RuntimeError(f"LLM error: {error_msg}")
    
    def _parse_comebacks(self, raw_response: str) -> list:
        """Parse the LLM response into structured comeback dicts."""
        comebacks = []
        
        style_map = {
            'SAVAGE': 'savage',
            'FUNNY': 'funny', 
            'COOL': 'cool_unbothered',
            'INTELLECTUAL': 'intellectual',
            'MOVIE': 'movie_reference'
        }
        
        lines = raw_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Ignore chatty filler lines
            lower_line = line.lower()
            if lower_line.startswith("here are") or lower_line.startswith("here is") or lower_line.startswith("sure") or lower_line.startswith("here's"):
                continue
            
            # Try to parse the structured format
            # Pattern: [STYLE_TAG] text |ACTOR_REF: name| OR | name |
            match = re.match(r'\[(SAVAGE|FUNNY|COOL|INTELLECTUAL|MOVIE)\]\s*(.+?)(?:\s*\|\s*(?:ACTOR_REF:\s*)?([^|]+?)\s*\|)?$', line, re.IGNORECASE)
            
            if match:
                style_key = style_map.get(match.group(1).upper(), 'savage')
                text = match.group(2).strip()
                actor_ref = match.group(3).strip() if match.group(3) and match.group(3).strip().lower() != 'none' else None
                
                config = self.STYLE_CONFIGS.get(style_key, {'emoji': '', 'label': 'Savage'})
                
                comebacks.append({
                    'text': text,
                    'style': style_key,
                    'style_label': config['label'],
                    'emoji': '',
                    'actor_ref': actor_ref
                })
            else:
                # Try looser parsing - any line with content
                # Remove numbering like "1." or "1)" or "- "
                cleaned = re.sub(r'^[\d]+[.)\-]\s*', '', line)
                cleaned = re.sub(r'^[-*•]\s*', '', cleaned)
                
                # Check if it has an actor ref appended anyway
                actor_match = re.search(r'(.*?)(?:\s*\|\s*(?:ACTOR_REF:\s*)?([^|]+?)\s*\|)$', cleaned, re.IGNORECASE)
                actor_ref = None
                if actor_match:
                    cleaned = actor_match.group(1).strip()
                    actor_ref = actor_match.group(2).strip()
                    if actor_ref.lower() == 'none':
                        actor_ref = None

                if len(cleaned) > 10:  # Minimum viable comeback length
                    # Clean up dangling pipes just in case
                    cleaned = re.sub(r'\s*\|\s*$', '', cleaned).strip()

                    comebacks.append({
                        'text': cleaned,
                        'style': 'savage',
                        'style_label': 'Savage',
                        'emoji': '',
                        'actor_ref': actor_ref
                    })
        
        return comebacks
    
    def _safety_filter(self, comebacks: list) -> list:
        """Remove comebacks that mention relatives or family."""
        filtered = []
        for comeback in comebacks:
            text_lower = comeback['text'].lower()
            is_safe = True
            for blocked in self.BLOCKED_WORDS:
                # Check for whole word match to avoid false positives
                if re.search(r'\b' + re.escape(blocked) + r'\b', text_lower):
                    is_safe = False
                    break
            if is_safe:
                filtered.append(comeback)
        return filtered
