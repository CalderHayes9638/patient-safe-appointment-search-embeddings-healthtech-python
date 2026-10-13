from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .guidance_index import GuidanceDocument, GuidanceIndex
from .notification_policy import NotificationAction, choose_notification


class GuidanceInput(BaseModel):
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)


class IndexRequest(BaseModel):
    documents: list[GuidanceInput] = Field(min_length=1)


class IndexResponse(BaseModel):
    indexed: int


class AppointmentRequest(BaseModel):
    patient_first_name: str = Field(min_length=1)
    appointment_time: str = Field(min_length=1)
    visit_type: str = Field(min_length=1)
    patient_note: str | None = None


class AppointmentResponse(BaseModel):
    action: NotificationAction
    message: str | None
    reason: str
    source_document_ids: list[str]


def create_service(index: GuidanceIndex | None = None) -> FastAPI:
    guidance = index or GuidanceIndex()
    app = FastAPI(title="Patient-safe appointment search")

    @app.post("/guidance", response_model=IndexResponse)
    def index_guidance(request: IndexRequest) -> IndexResponse:
        documents = [GuidanceDocument(**item.model_dump()) for item in request.documents]
        return IndexResponse(indexed=guidance.add(documents))

    @app.post("/appointments/notification", response_model=AppointmentResponse)
    def plan_notification(request: AppointmentRequest) -> AppointmentResponse:
        try:
            hits = guidance.search(f"Preparation instructions for {request.visit_type}")
        except IndexError as exc:
            raise HTTPException(status_code=409, detail="Index approved guidance before planning notifications") from exc
        decision = choose_notification(
            patient_first_name=request.patient_first_name,
            appointment_time=request.appointment_time,
            patient_note=request.patient_note,
            hits=hits,
        )
        return AppointmentResponse(**decision.__dict__)

    return app


app = create_service()
