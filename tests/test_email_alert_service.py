import json
from unittest.mock import MagicMock, patch

from src.alerts.email_alert_service import EmailAlertService
from src.domain.fusion_models import Evidence, FusionResult, RiskLevel


def _fusion_result():
    return FusionResult(
        risk_level=RiskLevel.MEDIUM,
        score=0.7,
        evidences=[Evidence(modality="text", description="Pedido de ajuda", confidence=0.9)],
        recommendations=["Avaliação humana prioritária."],
    )


def test_dispatch_simulates_and_writes_auditable_outbox_when_smtp_is_missing(tmp_path, monkeypatch):
    for key in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM", "ALERT_RECIPIENTS"):
        monkeypatch.delenv(key, raising=False)

    alert = EmailAlertService(tmp_path).dispatch(_fusion_result(), "Transcrição de teste")

    assert alert.status == "simulated"
    assert alert.outbox_path
    payload = json.loads((tmp_path / f"alert_{alert.alert_id}.json").read_text(encoding="utf-8"))
    assert payload["status"] == "simulated"
    assert "Transcrição de teste" in payload["body"]


def test_dispatch_sends_message_by_configured_smtp(tmp_path, monkeypatch):
    settings = {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USE_TLS": "true",
        "SMTP_USERNAME": "sender@example.com",
        "SMTP_PASSWORD": "app-password",
        "SMTP_FROM": "sender@example.com",
        "ALERT_RECIPIENTS": "doctor@example.com, nurse@example.com",
    }
    for key, value in settings.items():
        monkeypatch.setenv(key, value)
    smtp_client = MagicMock()
    smtp_client.__enter__.return_value = smtp_client

    with patch("src.alerts.email_alert_service.smtplib.SMTP", return_value=smtp_client) as smtp:
        alert = EmailAlertService(tmp_path).dispatch(_fusion_result(), "Transcrição de teste")

    assert alert.status == "sent"
    assert alert.recipients == ["doctor@example.com", "nurse@example.com"]
    smtp.assert_called_once_with("smtp.example.com", 587, timeout=20)
    smtp_client.starttls.assert_called_once()
    smtp_client.login.assert_called_once_with("sender@example.com", "app-password")
    smtp_client.send_message.assert_called_once()


def test_dispatch_captures_smtp_failure_without_raising(tmp_path, monkeypatch):
    for key, value in {
        "SMTP_HOST": "smtp.example.com", "SMTP_USERNAME": "sender@example.com",
        "SMTP_PASSWORD": "app-password", "SMTP_FROM": "sender@example.com",
        "ALERT_RECIPIENTS": "doctor@example.com",
    }.items():
        monkeypatch.setenv(key, value)

    with patch("src.alerts.email_alert_service.smtplib.SMTP", side_effect=OSError("network unavailable")):
        alert = EmailAlertService(tmp_path).dispatch(_fusion_result(), None)

    assert alert.status == "failed"
    assert "network unavailable" in alert.error
