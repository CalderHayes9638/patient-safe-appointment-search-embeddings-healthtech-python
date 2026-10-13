from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .guidance_index import SearchHit


class NotificationAction(str, Enum):
    SEND_REMINDER = "send_reminder"
    CLINICAL_REVIEW = "clinical_review"


@dataclass(frozen=True)
class NotificationDecision:
    action: NotificationAction
    message: str | None
    reason: str
    source_document_ids: list[str]


URGENT_TERMS = {"chest pain", "difficulty breathing", "fainted", "severe bleeding"}


def choose_notification(
    patient_first_name: str,
    appointment_time: str,
    patient_note: str | None,
    hits: list[SearchHit],
    minimum_score: float = 0.50,
) -> NotificationDecision:
    """Keep clinical uncertainty out of an automated operational reminder."""
    normalized_note = (patient_note or "").casefold()
    if any(term in normalized_note for term in URGENT_TERMS):
        return NotificationDecision(
            action=NotificationAction.CLINICAL_REVIEW,
            message=None,
            reason="Patient note contains a symptom that needs clinical review.",
            source_document_ids=[],
        )

    trusted = [hit for hit in hits if hit.score >= minimum_score]
    if not trusted:
        return NotificationDecision(
            action=NotificationAction.CLINICAL_REVIEW,
            message=None,
            reason="No sufficiently relevant approved guidance was retrieved.",
            source_document_ids=[],
        )

    guidance = trusted[0].document.text
    return NotificationDecision(
        action=NotificationAction.SEND_REMINDER,
        message=f"Hi {patient_first_name}, your appointment is {appointment_time}. {guidance}",
        reason="Reminder is grounded in approved appointment guidance.",
        source_document_ids=[hit.document.document_id for hit in trusted],
    )
