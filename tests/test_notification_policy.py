from appointment_search.guidance_index import GuidanceDocument, SearchHit
from appointment_search.notification_policy import NotificationAction, choose_notification


def test_urgent_patient_note_routes_to_clinical_review() -> None:
    hits = [
        SearchHit(
            document=GuidanceDocument(
                document_id="cardiology-arrival",
                title="Cardiology arrival",
                text="Please arrive 15 minutes early.",
            ),
            score=0.98,
        )
    ]

    decision = choose_notification(
        patient_first_name="Sam",
        appointment_time="Friday at 14:00",
        patient_note="I have chest pain today",
        hits=hits,
    )

    assert decision.action is NotificationAction.CLINICAL_REVIEW
    assert decision.message is None
    assert decision.source_document_ids == []


def test_relevant_guidance_produces_a_sourced_reminder() -> None:
    hits = [
        SearchHit(
            document=GuidanceDocument(
                document_id="imaging-prep",
                title="Imaging preparation",
                text="Bring a photo ID and medication list.",
            ),
            score=0.91,
        )
    ]

    decision = choose_notification("Riley", "Tuesday at 09:30", None, hits)

    assert decision.action is NotificationAction.SEND_REMINDER
    assert decision.source_document_ids == ["imaging-prep"]
    assert "Bring a photo ID" in (decision.message or "")


def test_live_range_match_passes_but_weak_match_requires_review() -> None:
    document = GuidanceDocument(
        document_id="imaging-prep-2026",
        title="Imaging appointment preparation",
        text="Arrive 20 minutes early and bring a photo ID and medication list.",
    )
    accepted = choose_notification("Riley", "Tuesday at 09:30", None, [SearchHit(document, 0.50554384234269)])
    rejected = choose_notification("Riley", "Tuesday at 09:30", None, [SearchHit(document, 0.49)])

    assert accepted.action is NotificationAction.SEND_REMINDER
    assert accepted.source_document_ids == ["imaging-prep-2026"]
    assert rejected.action is NotificationAction.CLINICAL_REVIEW
    assert rejected.source_document_ids == []
