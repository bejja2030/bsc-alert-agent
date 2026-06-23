# BSC Alert Agent 🏥📞

**Stop watching the terminal. Teach your agent to call you when it matters.**

> Voice AI Builder Challenge · DeepLearning.AI × Vocal Bridge · June 2026  
> **Author:** Ismail Bejja · Senior Nurse Manager, Oncology-Radiotherapy · GST TTA · Tanger, Morocco  
> **GitHub:** [bejja2030/bsc-alert-agent](https://github.com/bejja2030/bsc-alert-agent)

---

## The Problem

A *chef de service* in a public Moroccan oncology hospital cannot monitor BSC performance indicators while simultaneously managing clinical operations. When a critical indicator degrades — a patient consultation delay exceeding 14 days, a budget shortfall — the information sits in a spreadsheet until the monthly meeting.

**In oncology, every day of delay has direct clinical consequences.**

This is not a hypothetical. This agent was designed around a real service, real KPIs, and a real gap in public hospital management across francophone Africa.

---

## The Solution

Claude monitors the BSC dashboard and **decides autonomously** when to call the chef de service. It formulates a precise French-language `purpose`, injects it into a Vocal Bridge caller agent, and places the call via `vb call`.

```
BSC Monitor (Python)
      │
      ▼
Claude + make_phone_call tool       ← Leçon 4 pattern
      │  decides to call
      │  builds purpose in French
      ▼
Vocal Bridge CLI  →  vb call <numéro>
      ├── Foreground agent  (real-time French alert delivery)
      ├── Background agent  (context, corrective actions)
      └── Transcript → vb eval → score + prompt improvements  ← Leçon 5 pattern
```

---

## Live Demo Output

```
════════════════════════════════════════════════════════════
  BSC ALERT AGENT — Voice as a Tool
  Service Oncologie-Radiothérapie · GST TTA · Tanger
  Pattern : Leçon 4 (Vocal Bridge) · Claude + make_phone_call
════════════════════════════════════════════════════════════

  Mode DEMO    : OUI
  Chef service : +212600000000
  VB Agent ID  : bsc-alert-agent-v1

════════════════════════════════════════════════════════════
  BSC MONITOR · 23/06/2026 15:16:54
════════════════════════════════════════════════════════════
  🔴 C1    Délai médian demande → 1ère consultation       18.0 jours
  ✅ F1    Taux d'exécution budgétaire                    82.0 %
  ✅ RS1   Taux d'occupation du service                   78.0 %
  ✅ PI1   Conformité protocoles radiothérapie            88.0 %
  ✅ C5    Taux d'interruptions traitement (pannes)        2.1 %
────────────────────────────────────────────────────────────
  🚨 1 critique(s) · ⚠️  0 avertissement(s)
════════════════════════════════════════════════════════════

🤖 Claude analyse la situation et décide de l'action...
[Claude] Indicateur C1 en zone critique → make_phone_call

[VB] set_caller_purpose → Agent bsc-alert-agent-v1
     Purpose: Alerte BSC critique — Indicateur C1...

────────────────────────────────────────────────────────────
  📞 SIMULATION D'APPEL — Vocal Bridge
────────────────────────────────────────────────────────────
  Numéro     : +212600000000
  Call ID    : demo_call_1782220614

  Agent foreground (message vocal) :
  Alerte BSC critique — Service Oncologie-Radiothérapie GST TTA.
  Indicateur C1 : Délai médian demande → 1ère consultation.
  Valeur actuelle : 19 jours. Seuil d'alerte : 14 jours.
  Tendance : en dégradation depuis 3 semaines.
  Action requise : Activer le protocole de priorisation des
  consultations urgentes et contacter la coordination médicale
  dans les 48 heures.

  [VB] Bridge line : « Je vérifie les détails... »

  Agent background (contexte et recommandations) :
  • Parties à notifier : Chef AQP + Directeur établissement
  • Délai résolution : 48h (niveau critique)
  • Documentation : Rapport d'incident + plan correctif requis

  Chef de service : « Reçu. Je prends en charge immédiatement. »
────────────────────────────────────────────────────────────

✅ Appel effectué : demo_call_1782220614

[EVAL] Évaluation automatique — Leçon 5
{
  "score": 8.5,
  "verdict": "pass",
  "summary": "L'agent a correctement identifié l'alerte critique C1,
    formulé un message clair en français, et obtenu une confirmation
    du chef de service en moins de 90 secondes.",
  "what_worked": [
    "Message d'alerte précis avec valeur et seuil",
    "Bridge line naturelle sans silence mort",
    "Confirmation explicite de prise en charge"
  ],
  "suggested_prompt_improvements":
    "Ajouter la tendance des 3 dernières mesures dans le purpose
     pour contextualiser l'urgence."
}
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/bejja2030/bsc-alert-agent.git
cd bsc-alert-agent

# 2. Install
pip install anthropic

# 3. Run demo (no API keys needed)
python main.py --demo --once

# 4. Single check (reads current KPI values)
python main.py --once

# 5. Continuous monitoring (every 30s)
python main.py --interval 30

# 6. Evaluate a past call (Leçon 5 — Eval-Driven Development)
python main.py --eval demo_call_1782220614
```

### Production mode (with real phone calls)
```bash
# Requires Vocal Bridge Developer plan + Anthropic API key
set DEMO_MODE=false
set ANTHROPIC_API_KEY=sk-ant-...
set VOCAL_BRIDGE_API_KEY=vb_...

vb agent create \
  --name bsc-alert-agent-v1 \
  --style Chatty \
  --prompt-file prompts/caller_agent.txt

vb config set --outbound-enabled true --accept-outbound-tos

python main.py --once
```

---

## The 5 Monitored KPIs

| Code | Indicator | Target | Warning | Alert | Current | Status |
|------|-----------|--------|---------|-------|---------|--------|
| C1 | Délai demande → consultation | ≤ 7j | > 10j | > 14j | 18j | 🔴 |
| F1 | Taux d'exécution budgétaire | ≥ 85% | < 75% | < 70% | 82% | ✅ |
| RS1 | Taux d'occupation service | ≥ 80% | < 70% | < 65% | 78% | ✅ |
| PI1 | Conformité protocoles | ≥ 90% | < 80% | < 75% | 88% | ✅ |
| C5 | Interruptions traitement | ≤ 3% | > 6% | > 8% | 2.1% | ✅ |

KPIs are fully configurable via `data/kpis.json`. Any hospital can adapt this agent by editing that file alone.

---

## Architecture

### Pattern: Voice as a Tool (Leçon 4)

Claude receives a `make_phone_call` tool with a required `purpose` field.  
When a KPI turns critical, Claude:

1. **Reasons** about severity — the call is not hardcoded, Claude decides
2. **Builds** a precise French `purpose` including KPI id, current value, threshold, trend, and recommended action
3. **Injects** the purpose into the Vocal Bridge caller agent prompt via `set_caller_purpose()`
4. **Dials** via `vb call <numéro>` — Vocal Bridge handles the full telephony pipeline
5. **Returns** `{call_id, status}` to Claude — sanitized, no transport-level fields

### Concierge Architecture (Vocal Bridge)

| Layer | Role |
|-------|------|
| Foreground agent | Delivers the alert in real-time French, handles turn-taking |
| Background agent | Provides context, answers follow-up questions from the chef de service |
| Bridge line | `"Je vérifie les détails..."` — prevents dead silence during delegation |

### Eval-Driven Development (Leçon 5)

Every call triggers an automatic evaluation:
```bash
vb eval <session_id> \
  --objective "Alerter le chef de service et obtenir une confirmation" \
  --json
```
Returns: `score` (0–10), `verdict` (pass/fail), `what_worked`, `suggested_prompt_improvements`.  
The improvement loop: **build → call → eval → patch prompt → call → eval → ✓**

---

## Connection to the Course

| Course Concept | Implementation in this project |
|---------------|-------------------------------|
| Leçon 4 — Voice as a Tool | `make_phone_call` tool in Claude's toolbox, `vb call` CLI |
| Purpose-driven calling | `set_caller_purpose()` injects context before each call |
| Concierge Architecture | Foreground (alert) + Background (context + advice) |
| Leçon 5 — Eval-Driven Dev | `vb eval` after every call, automatic score + prompt suggestions |
| Agent-first principle | BSC monitor works as pure text agent first, voice added on top |
| Bridge line pattern | Immediate spoken acknowledgement prevents dead air |

---

## Why This Matters for LMIC Healthcare

Public hospital managers in Morocco and across francophone Africa lack:
- Real-time performance alert systems
- Tools adapted to French-language workflows
- Affordable alternatives to expensive BI platforms

This agent runs on a single Python file, requires no cloud infrastructure beyond an API key, and can be adapted to any hospital's KPIs by editing one JSON file. It demonstrates that Voice AI is not only for Silicon Valley — it belongs wherever a manager needs to act faster than the next monthly meeting.

---

## Project Structure

```
bsc-alert-agent/
├── main.py                   ← Claude agent + Vocal Bridge tool integration
├── src/
│   └── bsc_monitor.py        ← KPI monitoring, alert detection, dashboard
├── data/
│   ├── kpis.json             ← KPI definitions, thresholds, current values
│   └── call_log.json         ← Auto-generated call log
├── prompts/
│   ├── caller_agent.txt      ← Vocal Bridge caller agent prompt (French)
│   └── ai-agent.json         ← VB AI Agent integration config
└── README.md
```

---

## Author

**Ismail Bejja**  
Senior Nurse Manager (Infirmier Chef) · Oncology-Radiotherapy · GST TTA · Tanger, Morocco  
PhD Candidate · Management Hospitalier · Université Abdelmalek Essaâdi  
Published: *Bejja & Najdi, 2026 · Health SA Gesondheid · DOI: 10.4102/hsag.v31i0.3411*

---

*Voice AI Builder Challenge · DeepLearning.AI × Vocal Bridge · June 2026*
docs: professional README for challenge submission
