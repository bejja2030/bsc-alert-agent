"""
main.py — BSC Alert Agent
Pattern : Voice as a Tool (Leçon 4 — Vocal Bridge course)

Claude monitors BSC KPIs and calls the chef de service
when a critical indicator needs human intervention.

Usage:
    python main.py              # Monitor KPIs, Claude calls when needed
    python main.py --demo       # Simulate a KPI breach to trigger a call
    python main.py --once       # Single check and exit
    python main.py --eval <id>  # Run eval on a past call session

Voice AI Builder Challenge · DeepLearning.AI × Vocal Bridge · June 2026
Author: Ismail Bejja · University Oncology Hospital · Morocco
"""

import argparse
import json
import os
import sys
import time
import subprocess
from datetime import datetime

import anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from bsc_monitor import load_kpis, check_alerts, print_dashboard, get_summary_message


# ── Vocal Bridge caller agent prompt ─────────────────────────────────────────
def load_caller_prompt() -> str:
    """Load the Vocal Bridge caller agent base prompt."""
    prompt_path = os.path.join("prompts", "caller_agent.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback inline
    return """
    You are a hospital BSC monitoring agent calling on behalf of
    the oncology-radiotherapy service at GST TTA Tanger, Morocco.
    You speak French. You are professional, clear, and concise.
    Never fabricate medical information.
    Your sole purpose is to deliver BSC performance alerts to the chef de service.
    """


# ── Claude tool definition (Leçon 4 pattern) ─────────────────────────────────
MAKE_PHONE_CALL_TOOL = {
    "name": "make_phone_call",
    "description": (
        "Passe un appel téléphonique au chef de service pour signaler "
        "une alerte BSC critique nécessitant une intervention humaine. "
        "Utilise cet outil uniquement quand un indicateur est en zone rouge "
        "et qu'une action corrective immédiate est requise."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "Numéro de téléphone du chef de service (format E.164)"
            },
            "purpose": {
                "type": "string",
                "description": (
                    "Raison précise de l'appel — injectée dans le prompt de "
                    "l'agent appelant. Doit inclure : indicateur concerné, "
                    "valeur actuelle, seuil dépassé, action recommandée. "
                    "En français."
                )
            }
        },
        "required": ["phone_number", "purpose"]
    }
}


# ── Vocal Bridge CLI integration ──────────────────────────────────────────────
def set_caller_purpose(purpose: str, agent_id: str) -> None:
    """
    Inject the purpose into the caller agent's prompt before the call.
    Pattern from Leçon 4: same agent, different context per call.
    """
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if demo_mode:
        print(f"\n[VB] set_caller_purpose → Agent {agent_id}")
        print(f"     Purpose: {purpose[:100]}...")
        return

    # Real Vocal Bridge CLI
    subprocess.run([
        "vb", "agent", "update", agent_id,
        "--purpose", purpose
    ], check=True)


def place_call(phone_number: str, purpose: str, agent_id: str) -> dict:
    """
    Place the outbound call via Vocal Bridge CLI.
    From Leçon 4: vb call <numéro> triggers the full telephony pipeline.
    Returns: {call_id, status} — sanitized result for Claude.
    """
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    # Step 1: Inject purpose into caller agent prompt
    set_caller_purpose(purpose, agent_id)

    if demo_mode:
        # Simulate the call
        call_id = f"demo_call_{int(time.time())}"
        print(f"\n{'─'*60}")
        print("  📞 SIMULATION D'APPEL — Vocal Bridge (DEMO MODE)")
        print(f"{'─'*60}")
        print(f"  Numéro     : {phone_number}")
        print(f"  Call ID    : {call_id}")
        print(f"\n  Agent foreground (message vocal) :")
        print(f"  ─────────────────────────────────")

        # Simulate word-by-word delivery
        words = purpose.split()
        line = "  "
        for i, word in enumerate(words):
            line += word + " "
            if len(line) > 60:
                print(line)
                line = "  "
        if line.strip():
            print(line)

        print(f"\n  [VB] Bridge line : « Je vérifie les détails... »")
        print(f"\n  Agent background (contexte et recommandations) :")
        print(f"  ─────────────────────────────────────────────────")
        print(f"  • Parties à notifier : Chef AQP + Directeur établissement")
        print(f"  • Délai résolution : 48h (niveau critique)")
        print(f"  • Documentation : Rapport d'incident + plan correctif requis")
        print(f"\n  Chef de service : « Reçu. Je prends en charge immédiatement. »")
        print(f"  Statut appel : completed")
        print(f"{'─'*60}\n")

        # Save to log
        result = {
            "call_id": call_id,
            "status": "completed_demo",
            "timestamp": datetime.now().isoformat(),
            "purpose": purpose,
            "phone_number": phone_number
        }
        _save_call_log(result)
        return {"call_id": call_id, "status": "completed_demo"}

    # Real Vocal Bridge CLI call
    # vb call <numéro> — Vocal Bridge handles:
    # - SIP trunk, telephony bridge
    # - Foreground agent (real-time, low latency)
    # - Background agent (LLM reasoning, context)
    # - Transcript streaming
    # - Voicemail handling
    result = subprocess.run(
        ["vb", "call", phone_number, "--agent", agent_id, "--json"],
        capture_output=True, text=True, check=True
    )
    call_data = json.loads(result.stdout)

    clean_result = {
        "call_id": call_data.get("call_id"),
        "status": call_data.get("status")
    }
    _save_call_log({**clean_result, "purpose": purpose})
    return clean_result


def run_eval(session_id: str, objective: str) -> dict:
    """
    Eval-Driven Development (Leçon 5).
    vb eval <session_id> --objective "..." --json
    Returns: {score, verdict, summary, suggested_prompt_improvements}
    """
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        print(f"\n[VB EVAL] Session: {session_id}")
        print(f"[VB EVAL] Objectif: {objective}")
        eval_result = {
            "session_id": session_id,
            "objective": objective,
            "score": 8.5,
            "verdict": "pass",
            "summary": (
                "L'agent a correctement identifié l'alerte critique C1, "
                "formulé un message clair en français, et obtenu une confirmation "
                "du chef de service en moins de 90 secondes."
            ),
            "what_worked": [
                "Message d'alerte précis avec valeur et seuil",
                "Bridge line naturelle sans silence mort",
                "Confirmation explicite de prise en charge"
            ],
            "what_didnt": [
                "Pourrait mentionner le trend (dégradation vs amélioration)"
            ],
            "suggested_prompt_improvements": (
                "Ajouter la tendance des 3 dernières mesures dans le purpose "
                "pour que l'agent puisse contextualiser l'urgence."
            )
        }
        print(json.dumps(eval_result, ensure_ascii=False, indent=2))
        return eval_result

    # Real eval
    result = subprocess.run(
        ["vb", "eval", session_id, "--objective", objective, "--json"],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def _save_call_log(entry: dict) -> None:
    """Save call to log file."""
    log_path = "data/call_log.json"
    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except Exception:
                existing = []
    existing.append(entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


# ── Claude orchestration ──────────────────────────────────────────────────────
def run_claude_agent(alerts_summary: str, kpis_detail: str,
                     phone_number: str, agent_id: str) -> str:
    """
    Run Claude with make_phone_call tool.
    Claude decides whether to call and formulates the purpose.
    Pattern: agent-first (Leçon 3 principle applied to Leçon 4).
    """
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY", "demo_key")
    )

    system_prompt = """
    Tu es un agent de surveillance BSC pour un service d'oncologie-radiothérapie
    public au Maroc (GST TTA Tanger). Tu surveilles 5 indicateurs de performance
    et tu alertes le chef de service par appel téléphonique quand un indicateur
    est en zone critique (rouge).

    Règles :
    - N'appelle que si un indicateur est en zone ROUGE (critique).
    - Les indicateurs en zone JAUNE (avertissement) : log seulement, pas d'appel.
    - Formule un purpose précis en français : indicateur, valeur actuelle,
      seuil dépassé, tendance, action recommandée.
    - Un seul appel par cycle (l'indicateur le plus critique).
    """

    user_message = f"""
    Résultat de la surveillance BSC — {datetime.now().strftime('%d/%m/%Y %H:%M')} :

    {alerts_summary}

    Détail des indicateurs :
    {kpis_detail}

    Numéro chef de service : {phone_number}

    Analyse la situation et prends l'action appropriée.
    """

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        # Simulate Claude's reasoning and tool call
        print("\n[Claude] Analyse des alertes BSC...")
        time.sleep(0.5)
        print("[Claude] Indicateur C1 en zone critique → make_phone_call")

        # Simulate tool call
        purpose = (
            f"Alerte BSC critique — Service Oncologie-Radiothérapie GST TTA. "
            f"Indicateur C1 : Délai médian demande → 1ère consultation. "
            f"Valeur actuelle : 19 jours. Seuil d'alerte : 14 jours. "
            f"Tendance : en dégradation depuis 3 semaines. "
            f"Action requise : Activer le protocole de priorisation des "
            f"consultations urgentes et contacter la coordination médicale "
            f"dans les 48 heures."
        )

        result = place_call(phone_number, purpose, agent_id)
        print(f"\n[Claude] Appel terminé — {result['status']}")
        print(f"[Claude] Rapport transmis. Surveillance continue.")
        return f"Appel effectué : {result['call_id']}"

    # Real Claude API call with tool
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system_prompt,
        tools=[MAKE_PHONE_CALL_TOOL],
        messages=[{"role": "user", "content": user_message}]
    )

    # Process tool use
    for block in response.content:
        if block.type == "tool_use" and block.name == "make_phone_call":
            tool_input = block.input
            call_result = place_call(
                phone_number=tool_input["phone_number"],
                purpose=tool_input["purpose"],
                agent_id=agent_id
            )
            return f"Appel effectué : {call_result['call_id']} — {call_result['status']}"

    # No tool call — Claude decided not to call
    text_response = next(
        (b.text for b in response.content if hasattr(b, "text")), ""
    )
    return text_response


# ── Main loop ─────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="BSC Alert Agent — Claude calls you when a KPI needs attention"
    )
    p.add_argument("--demo",     action="store_true",
                   help="Simulate a KPI breach after 10s")
    p.add_argument("--once",     action="store_true",
                   help="Single check and exit")
    p.add_argument("--interval", type=int, default=30,
                   help="Monitoring interval in seconds (default: 30)")
    p.add_argument("--data",     default="data/kpis.json",
                   help="Path to KPI data file")
    p.add_argument("--eval",     metavar="SESSION_ID",
                   help="Run eval on a past call session")
    return p.parse_args()


def main():
    args = parse_args()

    print("\n" + "═"*60)
    print("  BSC ALERT AGENT — Voice as a Tool")
    print("  Service Oncologie-Radiothérapie · GST TTA · Tanger")
    print("  Pattern : Leçon 4 (Vocal Bridge) · Claude + make_phone_call")
    print("  Auteur  : Ismail ERRAI · 2026")
    print("═"*60)

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    print(f"\n  Mode DEMO    : {'OUI' if demo_mode else 'NON (production)'}")
    print(f"  Intervalle   : {args.interval}s")
    print(f"  Fichier KPIs : {args.data}")
    print()

    # Run eval mode
    if args.eval:
        objective = (
            "L'agent devait alerter le chef de service sur un indicateur BSC "
            "critique et obtenir une confirmation de prise en charge."
        )
        run_eval(args.eval, objective)
        return

    # Load config
    try:
        with open(args.data, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {args.data}")
        sys.exit(1)

    phone = config.get("chef_de_service", {}).get("phone", "+212600000000")
    agent_id = config.get("vb_agent_id", "bsc-alert-agent-v1")

    print(f"  Chef service : {phone}")
    print(f"  VB Agent ID  : {agent_id}")
    print("\n  Surveillance BSC démarrée...\n")

    demo_triggered = False
    elapsed = 0

    try:
        while True:
            # Load KPIs
            kpis, data = load_kpis(args.data)
            hospital = data.get("hospital", "Service Hospitalier")

            # Demo: trigger breach after 10s
            if args.demo and not demo_triggered and elapsed >= 10:
                print("🎬 DEMO: Simulation d'une dégradation des KPIs...")
                for kpi in kpis:
                    if kpi.id == "C1":
                        kpi.previous_value = kpi.current_value
                        kpi.current_value = 19.0
                demo_triggered = True

            alerts = check_alerts(kpis)
            print_dashboard(kpis, alerts)

            critical = [a for a in alerts if a.severity == "critical"]

            if critical:
                # Build context for Claude
                kpis_detail = "\n".join(
                    f"- {k.id} {k.label}: {k.current_value}{k.unit} "
                    f"(cible {k.direction}={k.target}{k.unit}, "
                    f"alerte={k.alert_threshold}{k.unit}, "
                    f"statut={k.status}, tendance={k.trend})"
                    for k in kpis
                )
                summary = get_summary_message(critical, hospital)

                print("🤖 Claude analyse la situation et décide de l'action...")
                result = run_claude_agent(
                    alerts_summary=summary,
                    kpis_detail=kpis_detail,
                    phone_number=phone,
                    agent_id=agent_id
                )
                print(f"\n✅ {result}")

                # Eval-Driven Development: run eval after each call
                if "call_id" in result or "demo_call" in result:
                    call_id = result.split(":")[-1].strip().split(" ")[0]
                    print(f"\n[EVAL] Évaluation automatique de l'appel...")
                    eval_objective = (
                        f"Alerter le chef de service sur l'indicateur critique "
                        f"et obtenir une confirmation de prise en charge."
                    )
                    run_eval(call_id, eval_objective)

                if args.demo and demo_triggered:
                    print("\n🎬 DEMO terminée avec succès !")
                    print("\nPour passer en production :")
                    print("  1. Créez un agent Vocal Bridge : vb agent create \\")
                    print("       --prompt prompts/caller_agent.txt \\")
                    print("       --style Chatty")
                    print("  2. Définissez DEMO_MODE=false")
                    print("  3. Définissez ANTHROPIC_API_KEY")
                    print("  4. Lancez : python main.py")
                    break

            elif alerts:
                print(f"⚠️  {len(alerts)} avertissement(s) — surveillance renforcée "
                      f"(appel non déclenché).")
            else:
                print("✅ Tous les KPIs nominaux. Aucune action requise.")

            if args.once:
                break

            print(f"  ⏱  Prochain contrôle dans {args.interval}s "
                  f"(Ctrl+C pour arrêter)\n")
            time.sleep(args.interval)
            elapsed += args.interval

    except KeyboardInterrupt:
        print("\n\n⛔ Surveillance arrêtée.")


if __name__ == "__main__":
    main()
