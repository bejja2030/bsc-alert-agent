# BSC Alert Agent 🏥📞

**Stop watching the terminal. Teach your agent to call you when it matters.**

Voice AI Builder Challenge · DeepLearning.AI × Vocal Bridge · June 2026
**Author:** Ismail ERRAI · Service Oncologie-Radiothérapie · GST TTA · Tanger, Morocco

---

## The Problem

A chef de service in a public Moroccan oncology hospital cannot monitor 5 BSC
performance indicators while managing clinical operations simultaneously.
When a critical indicator degrades — a patient delay exceeding 14 days,
a budget shortfall — the information sits in a spreadsheet until the monthly meeting.

**In oncology, every day of delay has clinical consequences.**

## The Solution — Voice as a Tool (Leçon 4 pattern)

Claude monitors the BSC dashboard and **decides autonomously** when to call.
It formulates a precise `purpose`, injects it into the Vocal Bridge caller agent,
and places the call via `vb call`.

```
BSC Monitor     →    Claude + make_phone_call tool    →    Vocal Bridge
(Python loop)        (decides to call, builds purpose)     vb call <numéro>
                                                            ├── Foreground agent (French, real-time)
                                                            ├── Background agent (context + advice)
                                                            └── Transcript → eval → log
```

## Quick Start

```bash
# Install
pip install anthropic

# Demo mode (no API keys needed)
python main.py --demo

# Single check
python main.py --once

# Continuous monitoring (every 30s)
DEMO_MODE=false \
ANTHROPIC_API_KEY=your_key \
python main.py

# Run eval on a past call (Eval-Driven Development — Leçon 5)
python main.py --eval demo_call_1234567890
```

## Vocal Bridge Setup (production)

```bash
# Install Vocal Bridge CLI
pip install vocalbridge

# Create the caller agent
vb agent create \
  --prompt prompts/caller_agent.txt \
  --style Chatty \
  --name bsc-alert-agent-v1

# Set your agent ID in data/kpis.json → "vb_agent_id"
```

## Architecture Details

### Pattern: Voice as a Tool (Leçon 4)

Claude is given a `make_phone_call` tool with a required `purpose` field.
When a KPI is critical, Claude:
1. Decides to call (not hardcoded — Claude reasons about severity)
2. Builds a precise French `purpose` with KPI values, threshold, trend, action
3. `set_caller_purpose()` injects purpose into the VB caller agent prompt
4. `vb call <numéro>` triggers the full telephony pipeline
5. Returns `{call_id, status}` to Claude (sanitized — no transport fields)

### Concierge Architecture (Vocal Bridge)
- **Foreground agent**: delivers the alert immediately in real-time French
- **Background agent**: reasons about context, answers follow-up questions
- **Bridge line**: "Je vérifie les détails..." prevents dead silence

### Eval-Driven Development (Leçon 5)
Every call is automatically evaluated:
```bash
vb eval <session_id> --objective "Alerter le chef de service..." --json
```
Returns: score (0-10), verdict (pass/fail), what worked, suggested improvements.

## The 5 Monitored KPIs

| Code | Indicator | Target | Alert |
|------|-----------|--------|-------|
| C1 | Délai demande → consultation | ≤ 7j | > 14j |
| F1 | Taux d'exécution budgétaire | ≥ 85% | < 70% |
| RS1 | Taux d'occupation service | ≥ 80% | < 65% |
| PI1 | Conformité protocoles | ≥ 90% | < 75% |
| C5 | Interruptions traitement | ≤ 3% | > 8% |

## Why This Matters for LMIC Healthcare

This agent addresses a real gap in public hospital management in Morocco and
across francophone Africa:
- Runs without cloud infrastructure (local Python)
- Uses open-source components where possible
- French language throughout
- Configurable for any hospital's KPIs (edit `data/kpis.json`)
- Eval-driven so quality improves over time

## Project Structure

```
bsc-alert-agent/
├── main.py                      ← Claude agent + VB tool integration
├── src/
│   └── bsc_monitor.py           ← KPI monitoring + alert detection
├── data/
│   ├── kpis.json                ← KPI definitions + current values
│   └── call_log.json            ← Auto-generated call log
├── prompts/
│   ├── caller_agent.txt         ← Vocal Bridge caller agent prompt
│   └── ai-agent.json            ← VB AI Agent integration config
├── specs/
│   └── mission.md               ← Full spec (Spec-Driven Development)
└── README.md
```

## Connection to the Course

| Course Pattern | Implementation |
|---------------|----------------|
| Leçon 4 — Voice as a Tool | `make_phone_call` tool in Claude, `vb call` CLI |
| Purpose-driven calling | `set_caller_purpose()` before each call |
| Concierge Architecture | Foreground (alert delivery) + Background (context) |
| Leçon 5 — Eval-Driven Dev | `vb eval` after every call, auto-improvement loop |
| Agent-first principle | BSC monitor works as text agent first |

---
*Voice AI Builder Challenge · DeepLearning.AI × Vocal Bridge · June 2026*
