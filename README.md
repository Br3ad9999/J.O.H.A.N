# 🔥 Savage Reply — AI Comeback Generator

> **Built for a friend who needed to fight back with words.**  
> Powered by open-source AI. Runs on your laptop. Accessible from your phone.

![Open Source](https://img.shields.io/badge/Open%20Source-AI%20Powered-orange?style=for-the-badge)
![Gemma](https://img.shields.io/badge/Gemma%202-Open%20Weight-blue?style=for-the-badge)
![Malayalam](https://img.shields.io/badge/Malayalam-Supported-green?style=for-the-badge)

---

## 🎯 What Is This?

**Savage Reply** is an AI-powered comeback generator that helps you respond to bullies with wit, humor, and devastating one-liners — in **English** and **Malayalam**.

Your friend gets bullied and doesn't know what to say back? Just record what the bully said (or type it), and the AI generates **multiple witty comebacks** in different styles. Pick your favorite, and optionally have the AI read it out loud.

### ✨ Features

- 🎤 **Voice Input** — Record what the bully said (supports English & Malayalam)
- ✍️ **Text Input** — Or just type it
- 🎬 **Movie References** — Comebacks inspired by iconic Malayalam cinema dialogues
- 🔥 **5 Comeback Styles** — Savage, Funny, Cool, Intellectual, Movie Reference
- 🤖 **Adaptive Tone** — AI matches the intensity of the insult automatically
- 🔊 **Text-to-Speech** — Hear your comeback read aloud in English or Malayalam
- 📱 **Phone-Friendly** — Access from any device via browser
- 🛡️ **Safe** — Never generates jokes about relatives/family (hard rule)
- 🔓 **Private** — Your conversations stay on your machine

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  🎤 Voice    │────▶│   Google     │────▶│                  │────▶│  📝 Text     │
│  Recording   │     │   STT        │     │   Gemma 2 9B     │     │  Comebacks   │
└──────────────┘     └──────────────┘     │  (Open-Weight)   │     └──────┬───────┘
                                          │                  │            │
┌──────────────┐                          │  + RAG Knowledge │     ┌──────▼───────┐
│  ✍️ Text     │─────────────────────────▶│    Base           │     │  🔊 edge-tts │
│  Input       │                          │                  │     │  (Free TTS)  │
└──────────────┘                          └──────────────────┘     └──────────────┘
                                                   ▲
                                          ┌────────┴────────┐
                                          │  📚 Knowledge   │
                                          │  Malayalam Movies│
                                          │  Memes & Culture │
                                          └─────────────────┘
```

---

## 🧰 Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| **LLM** | [Gemma 2 9B](https://ai.google.dev/gemma) via [Groq](https://groq.com) | Open-weight model for comeback generation |
| **Speech-to-Text** | Google Speech Recognition | Voice input transcription |
| **Text-to-Speech** | [edge-tts](https://github.com/rany2/edge-tts) | Free, high-quality TTS (Malayalam & English) |
| **Knowledge Base** | Custom RAG (JSON + Python) | Malayalam movies, memes, cultural references |
| **UI** | [Gradio](https://gradio.app) | Mobile-friendly web interface |
| **Runtime** | Python 3.8+ | Runs on any laptop/desktop |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- ffmpeg (for audio processing)
- Internet connection (for Groq API + TTS)

### 1. Clone & Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd savage_reply

# Run the one-click setup
chmod +x setup.sh
./setup.sh
```

### 2. Get Your Free API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free!)
3. Create an API key
4. Paste it in the `.env` file

### 3. Run!

```bash
source venv/bin/activate
python app.py
```

The app will show you a **public URL** you can open on your phone! 📱

---

## 📱 How to Use

1. **Open the app** on your phone or laptop browser
2. **Input the bully's message**:
   - 🎤 **Record Tab**: Hit record and speak what the bully said
   - ✍️ **Type Tab**: Just type it out
3. **Choose your settings**:
   - Reply Language: English, Malayalam, or Both
   - Number of comebacks (3-7)
   - Style: Adaptive (auto), Savage, Funny, Cool, Intellectual, or Movie Reference
4. **Hit "Generate Comebacks"** ⚡
5. **Pick your favorite** from the styled cards
6. **Optional**: Click "Read This Comeback" to hear it spoken aloud

---

## 🎬 Malayalam Cultural Knowledge

The AI draws from a curated knowledge base of:

- **30+ iconic movie dialogues** from Mohanlal, Mammootty, Suresh Gopi, Fahadh Faasil, Prithviraj, Dileep, and more
- **20+ Malayalam meme references** from Troll Malayalam, ICU, and internet culture
- **Actor-specific humor profiles** — channel your inner Mohanlal or Fahadh Faasil
- **Comeback templates** for each style, tuned for Malayalam sensibility

---

## 🔓 Why Open Source Matters

1. **Privacy First**: Your bully encounters stay on YOUR device. No conversation logs on anyone else's server.
2. **Cultural Authenticity**: Closed models don't understand Malayalam meme culture. We injected that knowledge ourselves through RAG.
3. **Customizable**: Swap the model (Gemma → Llama → Mistral) with one config change. Add your own movie dialogues. Tune the humor.
4. **Free Forever**: Groq's free tier + edge-tts = $0 operating cost.
5. **No Gatekeepers**: The open-weight Gemma model means no one can shut this down or change how it works.

---

## 🛡️ Safety

- ❌ **Never generates jokes about relatives** (mother, father, siblings, family — in English or Malayalam)
- ❌ **No threats of violence**
- ✅ **Adaptive intensity** — mild teasing gets funny responses, harsh attacks get dignified comebacks
- ✅ **Double-filtered** — LLM prompt + post-generation safety filter

---

## 📁 Project Structure

```
savage_reply/
├── app.py                      # Main Gradio application
├── core/
│   ├── __init__.py
│   ├── comeback_engine.py      # LLM-powered comeback generation
│   ├── tts_engine.py           # Text-to-speech (edge-tts)
│   └── stt_engine.py           # Speech-to-text
├── knowledge/
│   ├── __init__.py
│   ├── knowledge_base.py       # RAG knowledge retrieval
│   ├── malayalam_dialogues.json # Famous movie dialogues
│   ├── comeback_templates.json  # Comeback format templates
│   ├── meme_references.json     # Malayalam meme references
│   └── actor_styles.json        # Actor-specific humor styles
├── audio_cache/                 # Cached TTS audio files
├── requirements.txt
├── .env.example
├── setup.sh                    # One-click setup
└── README.md
```

---

## 🤝 Built For

This project was built for a real friend who faces bullying and needed a way to fight back — with words, not fists. Sometimes the best weapon is a well-timed comeback that makes everyone laugh.

> "The best revenge is massive success." — but until then, a savage comeback works too. 🔥

---

## 📜 License

MIT License — Use it, modify it, share it.

---

<p align="center">
  <b>🔥 Savage Reply</b> — Because every bully deserves a taste of their own medicine.<br>
  <i>Built with ❤️ using open-source AI</i>
</p>
