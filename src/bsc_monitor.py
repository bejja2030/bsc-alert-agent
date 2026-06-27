"""
bsc_monitor.py — BSC KPI Monitor & Alert Detection
BSC Alert Agent · Ismail Bejja · HPU Tanger · 2026

skill: kpi-status-classifier (reusable)
skill: alert-generator (reusable)
skill: bsc-score-aggregator (reusable)
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class KPI:
    id: str
    label: str
    unit: str
    direction: str
    target: float
    warn_threshold: float
    alert_threshold: float
    current_value: float
    previous_value: float
    source: str
    responsible: str
    recommendation: str

    @property
    def status(self) -> str:
        """skill: kpi-status-classifier"""
        v = self.current_value
        if self.direction == "max":
            if v >= self.warn_threshold:  return "green"
            if v >= self.alert_threshold: return "yellow"
            return "red"
        else:
            if v <= self.warn_threshold:  return "green"
            if v <= self.alert_threshold: return "yellow"
            return "red"

    @property
    def trend(self) -> str:
        delta = self.current_value - self.previous_value
        if self.direction == "max":
            if delta >  0.1: return "↑ en amélioration"
            if delta < -0.1: return "↓ en dégradation"
        else:
            if delta < -0.1: return "↑ en amélioration"
            if delta >  0.1: return "↓ en dégradation"
        return "→ stable"


@dataclass
class Alert:
    kpi: KPI
    severity: str
    triggered_at: datetime


def load_kpis(data_path: str = "data/kpis.json") -> tuple[list[KPI], dict]:
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    kpis = [KPI(**{k: v for k, v in kpi.items()
                   if k in KPI.__dataclass_fields__})
            for kpi in data["kpis"]]
    return kpis, data


def check_alerts(kpis: list[KPI]) -> list[Alert]:
    """skill: alert-generator"""
    alerts = []
    for kpi in kpis:
        if kpi.status in ("yellow", "red"):
            severity = "critical" if kpi.status == "red" else "warning"
            alerts.append(Alert(
                kpi=kpi,
                severity=severity,
                triggered_at=datetime.now()
            ))
    return alerts


def get_summary_message(alerts: list[Alert], hospital: str) -> str:
    critical = [a for a in alerts if a.severity == "critical"]
    warnings  = [a for a in alerts if a.severity == "warning"]
    if not alerts:
        return f"BSC nominal — {hospital}. Aucun indicateur en alerte."
    parts = [f"Rapport BSC — {hospital}."]
    if critical:
        parts.append(
            f"{len(critical)} indicateur(s) critique(s) : "
            f"{', '.join(a.kpi.id for a in critical)}."
        )
    if warnings:
        parts.append(
            f"{len(warnings)} avertissement(s) : "
            f"{', '.join(a.kpi.id for a in warnings)}."
        )
    return " ".join(parts)


def print_dashboard(kpis: list[KPI], alerts: list[Alert]) -> None:
    icons = {"green": "✅", "yellow": "⚠️ ", "red": "🔴"}
    print("\n" + "═"*60)
    print(f"  BSC MONITOR · {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("═"*60)
    for k in kpis:
        print(f"  {icons[k.status]} {k.id:<5} "
              f"{k.label:<44} {k.current_value:>6.1f}{k.unit}")
    print("─"*60)
    c = sum(1 for a in alerts if a.severity == "critical")
    w = sum(1 for a in alerts if a.severity == "warning")
    if alerts:
        print(f"  🚨 {c} critique(s) · ⚠️  {w} avertissement(s)")
    else:
        print("  ✅ Tous les KPIs dans les seuils.")
    print("═"*60 + "\n")
