# BSC Alert Agent — Mission Spec
## Voice AI Builder Challenge · DeepLearning.AI × Vocal Bridge · June 2026

**Author:** Ismail ERRAI
Nurse Manager · Quality & Performance Officer
Oncology-Radiotherapy · GST TTA · Tanger, Morocco

---

## THE MISSION

Stop watching the terminal.
Teach your AI agent to call you when it matters.

In a public oncology hospital in Morocco, a chef de service cannot monitor
5 BSC performance indicators while managing clinical operations.
When a critical indicator drops — a patient delay, a budget gap —
the information sits in a spreadsheet until the monthly review.

This agent changes that. It monitors the BSC and calls the chef de service
the moment a KPI enters the danger zone.

---

## ARCHITECTURE

Pattern: Voice as a Tool (Leçon 4 — Vocal Bridge course)

BSC Monitor → Claude + make_phone_call tool → Vocal Bridge vb call
- Foreground agent: delivers alert in real-time French
- Background agent: provides context and recommendations
- Transcript → vb eval → improvement loop

---

## THE 5 MONITORED KPIs

| Code | Indicator | Target | Alert |
|------|-----------|--------|-------|
| C1 | Délai demande → consultation | ≤ 7j | > 14j |
| F1 | Taux d'exécution budgétaire | ≥ 85% | < 70% |
| RS1 | Taux d'occupation service | ≥ 80% | < 65% |
| PI1 | Conformité protocoles | ≥ 90% | < 75% |
| C5 | Interruptions traitement | ≤ 3% | > 8% |

---

## SUCCESS CRITERIA

- KPI breach detected within one monitoring cycle
- Claude decides autonomously to call (not hardcoded)
- French voice alert delivered with value, threshold, trend, action
- Eval score ≥ 7/10 on every call
- Full transcript logged for audit trail

---

## CONNECTION TO THE COURSE

| Course Pattern | Implementation |
|---------------|----------------|
| Leçon 4 — Voice as a Tool | make_phone_call tool, vb call CLI |
| Purpose-driven calling | set_caller_purpose() before each call |
| Concierge Architecture | Foreground + Background agents |
| Leçon 5 — Eval-Driven Dev | vb eval after every call |
| Agent-first principle | Text agent works before adding voice |

---

*Built following Spec-Driven Development methodology*
*(DeepLearning.AI × JetBrains course, April 2026)*
*© 2026 Ismail ERRAI · GST TTA · Tanger, Morocco*
