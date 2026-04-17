# GemmaChat

A local chat interface for [Gemma](https://ollama.com/library/gemma4) models served by [Ollama](https://ollama.com). Comes in two flavours:

| Mode | Entry point | Description |
|------|-------------|-------------|
| **Terminal** | `start_chat.sh` | Rich TUI using `rich` |
| **Web** | `web_app/start_web.sh` | Django web app with image support |

---

## Requirements

| Dependency | Notes |
|------------|-------|
| Python ≥ 3.11 | `python3 --version` |
| [Ollama](https://ollama.com/download) | Must be running (`ollama serve`) |
| `gemma4:e2b` model | `ollama pull gemma4:e2b` |

---

## Quick start

### 1 — Pull the model

```bash
ollama pull gemma4:e2b
```

### 2 — Terminal chat

```bash
bash start_chat.sh
```

Slash commands available inside the chat:

| Command | Effect |
|---------|--------|
| `/clear` | Wipe conversation history |
| `/exit` | Quit |

### 3 — Web chat

```bash
bash web_app/start_web.sh
```

The server starts in the background on **http://127.0.0.1:8000** and logs to `web_app/gemmachat_web.log`.

```bash
# Check logs
tail -f web_app/gemmachat_web.log

# Stop the server
kill $(cat web_app/gemmachat_web.pid)
```

Environment variables to override defaults:

```bash
HOST=0.0.0.0 PORT=9000 bash web_app/start_web.sh
```

---

## Web UI features

- **Streaming responses** — tokens appear in real time via Server-Sent Events
- **Image attachment** — attach a JPEG / PNG / GIF / WebP (≤ 10 MB) directly in the prompt
- **Markdown rendering** — assistant replies are rendered with full Markdown support (code blocks, tables, lists)
- **Persistent history** — conversation is stored in a server-side file session; survives page reloads
- **Clear conversation** — one-click button to reset the session

---

## Project structure

```
GemmaChat/
├── local_gemma.py          # Terminal chat client
├── start_chat.sh           # Launcher for the terminal client
├── requirements.txt        # Terminal client dependencies
│
└── web_app/
    ├── manage.py
    ├── start_web.sh        # Background launcher (logs to gemmachat_web.log)
    ├── run_linters.sh      # Runs black · isort · flake8 · ruff · pylint · mypy
    ├── requirements.txt    # Web app dependencies
    │
    ├── domain/             # Innermost ring — zero external dependencies
    │   ├── entities.py     # Message, Conversation dataclasses
    │   └── ports.py        # ChatGateway abstract port
    │
    ├── application/        # Use-cases — depends only on domain
    │   └── chat_service.py # ChatService.send() streams a reply
    │
    ├── infrastructure/     # Adapters — implements domain ports
    │   └── ollama_gateway.py  # OllamaGateway → local Ollama server
    │
    └── chat/               # Presentation layer (Django app)
        ├── views.py        # chat_page · stream_chat · clear_history
        ├── urls.py
        └── templates/chat/index.html
```

The web app follows **Clean Architecture**: `domain` ← `application` ← `infrastructure` / `chat`. Swapping the LLM backend requires only a new `ChatGateway` implementation.

---

## Code quality

Run all linters from the `web_app/` directory:

```bash
bash web_app/run_linters.sh
```

Tools used: **black**, **isort**, **flake8**, **ruff**, **pylint** (10.00 / 10), **mypy**.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | dev key | Set in production |
| `DJANGO_DEBUG` | `true` | Set to `false` in production |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated list |
| `HOST` | `127.0.0.1` | Bind address for `start_web.sh` |
| `PORT` | `8000` | Port for `start_web.sh` |

---

## License

MIT
