import json
import os
import smtplib
import ssl
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional

from src.domain.alert_models import AlertNotification
from src.domain.fusion_models import FusionResult


class EmailAlertService:
    """Envia alertas por SMTP ou cria uma saída simulada para demonstração."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    @staticmethod
    def _recipients() -> List[str]:
        return [item.strip() for item in os.getenv("ALERT_RECIPIENTS", "").split(",") if item.strip()]

    @staticmethod
    def _configured(recipients: List[str]) -> bool:
        required = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM")
        return bool(recipients) and all(os.getenv(item) for item in required)

    @staticmethod
    def _format_body(alert_id: str, timestamp: str, fusion_result: FusionResult, transcript: Optional[str]) -> str:
        evidences = fusion_result.evidences or []
        recommendations = fusion_result.recommendations or []
        lines = [
            "ALERTA DE APOIO À TRIAGEM — requer avaliação humana.",
            "Esta mensagem não contém diagnóstico e não substitui um profissional de saúde.",
            "",
            f"ID do alerta: {alert_id}",
            f"Data/hora: {timestamp}",
            f"Nível de risco: {fusion_result.risk_level.value}",
            f"Score: {fusion_result.score}",
            "",
            "Evidências:",
        ]
        lines.extend(
            f"- [{evidence.modality}] {evidence.description} (confiança: {evidence.confidence:.2f})"
            for evidence in evidences
        ) or lines.append("- Nenhuma evidência detalhada disponível.")
        lines.append("")
        lines.append("Recomendações:")
        lines.extend(f"- {recommendation}" for recommendation in recommendations) or lines.append("- Sem recomendações.")
        if transcript:
            lines.extend(["", "Transcrição:", transcript])
        return "\n".join(lines)

    def dispatch(self, fusion_result: FusionResult, transcript: Optional[str]) -> AlertNotification:
        alert_id = uuid.uuid4().hex
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        recipients = self._recipients()
        body = self._format_body(alert_id, timestamp, fusion_result, transcript)

        if not self._configured(recipients):
            self.output_dir.mkdir(parents=True, exist_ok=True)
            outbox_path = self.output_dir / f"alert_{alert_id}.json"
            payload = {
                "alert_id": alert_id,
                "created_at": timestamp,
                "channel": "email",
                "status": "simulated",
                "recipients": recipients,
                "subject": f"[Triagem] Alerta {fusion_result.risk_level.value} — {alert_id[:8]}",
                "body": body,
                "reason": "Configuração SMTP ausente; envio simulado para demonstração.",
            }
            outbox_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            return AlertNotification(
                alert_id=alert_id, created_at=timestamp, channel="email", status="simulated",
                recipients=recipients, outbox_path=str(outbox_path),
            )

        message = EmailMessage()
        message["Subject"] = f"[Triagem] Alerta {fusion_result.risk_level.value} — {alert_id[:8]}"
        message["From"] = os.environ["SMTP_FROM"]
        message["To"] = ", ".join(recipients)
        message.set_content(body)

        try:
            port = int(os.getenv("SMTP_PORT", "587"))
            use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes"}
            with smtplib.SMTP(os.environ["SMTP_HOST"], port, timeout=20) as client:
                if use_tls:
                    client.starttls(context=ssl.create_default_context())
                client.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
                client.send_message(message)
            return AlertNotification(
                alert_id=alert_id, created_at=timestamp, channel="email", status="sent", recipients=recipients,
            )
        except Exception as exc:
            return AlertNotification(
                alert_id=alert_id, created_at=timestamp, channel="email", status="failed", recipients=recipients,
                error=str(exc),
            )
