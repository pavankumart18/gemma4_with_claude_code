# Gemma 4 + Claude Code via Ollama

Run Claude Code against local or cloud-hosted alternative models, with zero Anthropic API calls.

---

## How it works

Ollama v0.14+ exposes an **Anthropic-compatible Messages API** at `http://localhost:11434`. Claude Code's `ANTHROPIC_BASE_URL` env var redirects its requests there. Third-party providers (Moonshot/Kimi, etc.) expose the same Anthropic-compatible API format at their own endpoints — no Ollama required for those.

---

## Path A — Local models via Ollama (chat/codegen only)

### Requirements

- Windows 10/11 (or macOS/Linux)
- 8 GB+ free disk space, 16 GB RAM recommended
- No GPU required — faster with CUDA/Metal GPU

### 1. Install Ollama

**Windows:**
```powershell
winget install Ollama.Ollama
```

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

```bash
ollama --version   # should show 0.14.0 or later
```

### 2. Pull Gemma 4

```bash
ollama pull gemma4:e2b   # 7.2 GB, 128K context
```

| Tag | Size | Context | Notes |
|-----|------|---------|-------|
| `gemma4:e2b` | 7.2 GB | 128K | Best for laptops |
| `gemma4:e4b` | 9.6 GB | 128K | Default tag |
| `gemma4:26b` | 18 GB | 256K | Workstation GPU |
| `gemma4:31b` | 20 GB | 256K | Dense, highest quality |

### 3. Configure and launch Claude Code

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_BASE_URL   = "http://localhost:11434"
$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_API_KEY    = ""
claude --model gemma4:e2b
```

**macOS / Linux:**
```bash
ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" claude --model gemma4:e2b
```

Or use Ollama's one-step shortcut:
```bash
ollama launch claude --model gemma4:e2b
```

---

## Path B — Kimi K2.5 via Moonshot API (agentic tool use)

If you need Claude Code to actually **write files, run commands, and use tools**, local Gemma 4 won't cut it (see test results below). Kimi K2.5 routes through Moonshot AI's cloud and has proper Anthropic-format tool calling — **no Ollama needed**.

### 1. Get a free Moonshot API key

Sign up at [platform.kimi.ai](https://platform.kimi.ai) → API Keys → Create API Key.

### 2. Configure Claude Code

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_BASE_URL   = "https://api.moonshot.ai/anthropic"
$env:ANTHROPIC_AUTH_TOKEN = "sk-your-moonshot-key-here"
$env:ANTHROPIC_API_KEY    = ""
claude --model kimi-k2.5
```

**macOS / Linux:**
```bash
export ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-your-moonshot-key-here"
export ANTHROPIC_API_KEY=""
claude --model kimi-k2.5
```

> Note: `kimi-k2.5:cloud` via Ollama also works but requires setting `MOONSHOT_API_KEY` in Ollama's server environment — using Moonshot's endpoint directly is simpler.

---

## Test results — what actually works

Tested on Windows 11, Ollama v0.23.3, May 2026:

| Feature | `gemma4:e2b` | `gemma4:31b` | `qwen3-coder:30b` | `kimi-k2.5:cloud` |
|---------|:-----------:|:-----------:|:----------------:|:----------------:|
| Chat / Q&A | ✅ | ✅ | ✅ | ✅ |
| Code generation | ✅ | ✅ | ✅ | ✅ |
| One-shot `-p` prompts | ✅ | ✅ | ✅ | ✅ |
| Streaming | ✅ | ✅ | ✅ | ✅ |
| Image input | ✅ | ✅ | ➖ | ✅ |
| **Agentic tool use** | ❌ | ⚠️ | ⚠️ | ✅ (needs API key) |
| **File write/read** | ❌ | ❌ | ❌ | ✅ (needs API key) |

### Why local models fail at tool use

Claude Code sends tool definitions in Anthropic's JSON schema format and expects `tool_use` blocks back. Local models respond in their own native formats instead:

- **`gemma4:e2b`** — ignores tool definitions entirely, answers in plain text
- **`gemma4:31b`** — knows it should act, generates bash heredoc as text
- **`qwen3-coder:30b`** — outputs `<function=Write>` XML (correct intent, wrong wire format)

Ollama's Anthropic-compatibility layer doesn't translate these native formats into `tool_use` blocks for local models. The result: Claude Code never receives a parseable tool call.

### Code generation quality

**gemma4:e2b** — verbose, handles edge cases:
```python
def is_palindrome(s: str) -> bool:
    processed_s = "".join(filter(str.isalnum, s)).lower()
    return processed_s == processed_s[::-1]
```

**gemma4:31b / qwen3-coder:30b** — concise:
```python
def is_palindrome(s): return s == s[::-1]
```

Response time: ~8–15s first token on CPU, faster on GPU.

---

## Gotchas

1. **Local models = chat only** — Gemma 4 and qwen3-coder work well for Q&A and code generation but cannot perform agentic tasks (file edits, running commands, multi-step automation).
2. **Cloud models need their own API key** — `kimi-k2.5:cloud` via Ollama returns 401 until you set `MOONSHOT_API_KEY` in Ollama's environment. Easier to use Moonshot's endpoint directly (Path B above).
3. **`ANTHROPIC_API_KEY` must be explicitly empty** — set it to `""`, not unset; Claude Code errors if the var is missing when `ANTHROPIC_BASE_URL` is overridden.
4. **`--model` is required** — Claude Code defaults to Anthropic model IDs; always pass `--model gemma4:e2b` (or whichever tag).
5. **First response is slow on CPU** — ~30–60s for model to load into RAM; subsequent turns are faster.
6. **stdin warning on Windows** — `Warning: no stdin data received in 3s` is harmless.

---

## Tested environment

- OS: Windows 11 Pro (10.0.26200)
- Ollama: v0.23.3
- Models: `gemma4:e2b` (7.2 GB), `gemma4:31b` (19 GB), `qwen3-coder:30b` (18 GB), `kimi-k2.5:cloud`
- Claude Code: claude-sonnet-4-6
- Date: May 2026

---

## References

- [Ollama × Claude Code integration docs](https://docs.ollama.com/integrations/claude-code)
- [Use Kimi K2.5 in Claude Code — Kimi API Platform](https://platform.kimi.ai/docs/guide/agent-support)
- [gemma4 on Ollama library](https://ollama.com/library/gemma4)
- [Gemma 4 — Google DeepMind](https://deepmind.google/models/gemma/gemma-4/)
- [qwen3-coder on Ollama library](https://ollama.com/library/qwen3-coder)
- [kimi-k2.5 on Ollama library](https://ollama.com/library/kimi-k2.5)
