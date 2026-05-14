# AI Whatsapp Bot

Local AI-powered WhatsApp auto-reply assistant with intent classification, personality-aware response generation, safety filtering, and browser automation.

## Features

* Local LLM inference using Ollama
* WhatsApp Web automation with Selenium
* Intent classification for different message types
* Personality-conditioned response generation
* Rule-based safety filtering
* Automatic reply suppression for conversation-ending messages
* Hebrew-focused conversational behavior
* FastAPI backend API

## Example

Incoming:

```text
למה את לא עונה??
```

Generated reply:

```text
הכל בסדר פשוט קצת עסוקה :)
```

---

## Tech Stack

* Python
* Ollama
* Selenium
* FastAPI
* Local LLMs
* Chromium / Chrome

---

## Current Intents

* worried
* mom
* location
* invite
* pushy
* short
* general
* stop

---

## Architecture

```text
WhatsApp Web
      ↓
Selenium Bot
      ↓
FastAPI Backend
      ↓
Intent Classification
      ↓
LLM Response Generation
      ↓
Safety Filtering + Ranking
      ↓
Suggested Reply
```

---

## Setup

### 1. Clone repository

```bash
git clone <repo-url>
cd busy-but-alive
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

https://ollama.com/

Pull a model:

```bash
ollama pull aminadaven/dictalm2.0-instruct:q4_k_m
```

Start Ollama:

```bash
ollama serve
```

### 4. Start FastAPI backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0
```

### 5. Run WhatsApp bot

```bash
python app/whatsapp_bot.py
```

Scan the WhatsApp QR code when prompted.

---

## Notes

* Designed primarily for Hebrew conversations
* Uses local inference only
* Intended as a personal AI assistant / research project
* Selenium selectors may require updates if WhatsApp Web changes

---

## Future Improvements

* Better Hebrew conversational tuning
* Multi-contact support
* Delayed / human-like responses
* UI for reply approval
* Smarter memory and conversation context
* Fine-tuned local models
