from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AlertNotification:
    """Registro auditável do encaminhamento de um resultado à equipe médica."""

    alert_id: str
    created_at: str
    channel: str
    status: str  # sent, simulated, failed
    recipients: List[str] = field(default_factory=list)
    error: Optional[str] = None
    outbox_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "alert_id": self.alert_id,
            "created_at": self.created_at,
            "channel": self.channel,
            "status": self.status,
            "recipients": self.recipients,
        }
        if self.error:
            result["error"] = self.error
        if self.outbox_path:
            result["outbox_path"] = self.outbox_path
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertNotification":
        return cls(
            alert_id=data["alert_id"],
            created_at=data["created_at"],
            channel=data["channel"],
            status=data["status"],
            recipients=data.get("recipients", []),
            error=data.get("error"),
            outbox_path=data.get("outbox_path"),
        )
