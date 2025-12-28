# veritas-ai
Fact Checking AI
Here is the complete `README.md` content in a single copy-pasteable block.

```markdown
# 🔍 Veritas AI: Multi-Agent Fact-Checking System

**Author:** Aswin A S  
**Powered by:** Google Gemini & Streamlit

## 📖 Overview
Veritas AI is an automated, multi-agent fact-checking system designed to combat misinformation. Given a URL (news article or video) or plain text, the system uses a pipeline of AI agents to extract claims, gather evidence, and verify accuracy using the Google Gemini API.

It replaces slow manual verification with a high-speed, automated workflow capable of handling text articles, YouTube videos, and raw text input.

## 🤖 System Architecture

The system utilizes a sequential multi-agent architecture where data flows through specialized processing units:

```
                    ┌──────────────────────────┐
                    │        USER INPUT        │
                    │       (URL or Text)      │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │  ARTICLE EXTRACTOR       │
                    │ (Trafilatura/newspaper)  │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   AGENT 1: CLAIM EXTRACT │
                    │   (Gemini 2.5 Flash)     │
                    └─────────────┬────────────┘
                                  │
                   Claims → → → → │
                                  ▼
                    ┌──────────────────────────┐
                    │ AGENT 2: EVIDENCE HUNTER │
                    │   (Gemini synthetic)     │
                    └─────────────┬────────────┘
                                  │
                  Evidence → → →  │
                                  ▼
                    ┌──────────────────────────┐
                    │ AGENT 3: VERIFIER        │
                    │  (supported/contradicted │
                    │       /inconclusive)     │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ AGENT 4: REPORTER        │
                    │ (summary + confidence)   │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │  FINAL FACT-CHECK REPORT │
                    └──────────────────────────┘

```

## ✨ Key Features & Concepts

This project implements advanced AI engineering concepts:

* **Sequential Multi-Agent System:** Tasks are divided among specialized agents (Extractor → Hunter → Verifier → Reporter).
* **Multi-Modal Input:** Handles Text URLs, YouTube/Shorts URLs (via `yt-dlp` & `ffmpeg`), and plain text.
* **Custom Tool Integration:** Uses `Trafilatura` for web scraping and `YouTubeTranscriptApi` for video data.
* **Loop Logic:** Includes fallback mechanisms (e.g., trying captions first, then falling back to audio transcription).
* **Context Engineering:** Sophisticated prompting strategies to filter opinions and isolate verifiable facts.

## 🛠️ Agents Breakdown

| Agent | Role | Technology |
| --- | --- | --- |
| **Claim Extractor** | Identifies 3-5 verifiable facts, filtering out opinions. | Gemini Flash |
| **Evidence Hunter** | Synthesizes internal knowledge to check claims. | Gemini Flash |
| **Verifier** | Classifies claims as **SUPPORTED**, **CONTRADICTED**, or **INCONCLUSIVE**. | Gemini Flash |
| **Reporter** | Aggregates findings into a "Cyber-Intelligence" summary. | Gemini Flash |

## ⚙️ Installation & Setup

### Prerequisites

* **Python 3.8+**
* **FFmpeg** (Required for video/audio processing)
* *Windows:* Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract, and add `bin` folder to System PATH.



### 1. Clone the Repository

```bash
git clone [https://github.com/ASWINdevop/veritas-ai.git](https://github.com/ASWINdevop/veritas-ai.git)
cd veritas-ai

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Configure Secrets

Create a file named `.streamlit/secrets.toml` in the project root directory:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_google_api_key_here"

```

### 4. Run the Application

```bash
streamlit run app.py

```

## 📦 Tech Stack

* **Frontend:** Streamlit
* **AI Core:** Google Gemini API (1.5 Flash)
* **Audio/Video:** `yt-dlp`, `ffmpeg`, `Wait-for-it` (Whisper Tiny)
* **Scraping:** `trafilatura`, `BeautifulSoup4`

---

*Built as a capstone project for the Google Gemini AI Course.*

```

```
