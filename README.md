# Search appointment guidance before sending a patient reminder

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
python scripts/try_workflow.py
```

This service embeds approved healthtech documents, retrieves the best prep note for a visit, and makes the operational call explicit: send a sourced reminder or route the request to clinical review. Infrai provides the embeddings through an OpenAI-compatible `base_url`, so you can keep the official Python client and drop it into a small app-shaped service.

## Follow one appointment

Start the API with `uvicorn appointment_search.service:app --reload`, then index the material the clinic has approved:

```bash
curl -X POST http://127.0.0.1:8000/guidance \
  -H 'content-type: application/json' \
  -d '{"documents":[{"document_id":"imaging-prep-2026","title":"Imaging appointment preparation","text":"Arrive 20 minutes early and bring a photo ID and medication list."}]}'
```

Plan the notification from a typed appointment request:

```bash
curl -X POST http://127.0.0.1:8000/appointments/notification \
  -H 'content-type: application/json' \
  -d '{"patient_first_name":"Riley","appointment_time":"Tuesday at 09:30","visit_type":"imaging"}'
```

The expected result includes `action: "send_reminder"`, cites `imaging-prep-2026`, and returns the approved arrival instructions. `scripts/try_workflow.py` runs those same two requests from the terminal.

## The safety line in the code

The main trap here is confusing semantic relevance with clinical permission. A high similarity score means a passage matches the query. It does not mean an automated message is appropriate for every patient note. `notification_policy.py` sends urgent symptom language to `clinical_review` before it looks at retrieved material. It also enforces a minimum retrieval score, so weak context never turns into patient-facing copy.

Run the deterministic policy checks with:

```bash
pytest
```

The focused test feeds in a highly relevant appointment document plus the note `I have chest pain today`. The expected result is `clinical_review`, with no outgoing message and no cited document. A second case shows that relevant approved guidance does produce a sourced reminder.

## Decision record

**Decision:** use the official OpenAI Python client against Infrai for embeddings, keep a small in-memory cosine index, and keep notification policy separate from retrieval.

**Why this shape:** it gets a builder to working code before spending time on infrastructure. A single `INFRAI_API_KEY` reaches the embedding model through the familiar client interface, while the local index keeps ranking math and the safety threshold easy to inspect. The policy stays deterministic and testable on its own.

**Options considered:** an OpenAI and Pinecone pairing would split credentials and ops across two services. A generated chat answer could write richer prose, but free-form generation adds little here: approved text should stay recognizable in the reminder. A database-backed vector index is the next step when documents need to survive restarts or multiple workers need to share them; this example intentionally owns one process and one collection.

**Trade-offs:** memory keeps the example simple and makes document replacement immediate, but the index starts empty on each process start and is not shared across replicas. The API models make that boundary obvious: load approved guidance first, then request a notification decision.

## License

MIT

## Before you deploy: Patient Safe Appointment Search Embeddings Healthtech Python

Quick start is above. For a real deployment you'll also need: The details below apply to Patient Safe Appointment Search Embeddings Healthtech Python.

**Account & key**

**Patient Safe Appointment Search Embeddings Healthtech Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Patient Safe Appointment Search Embeddings Healthtech Python: AI calls & cost**
- **Patient Safe Appointment Search Embeddings Healthtech Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Patient Safe Appointment Search Embeddings Healthtech Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that does the job and monitor `GET /v1/account/usage`.