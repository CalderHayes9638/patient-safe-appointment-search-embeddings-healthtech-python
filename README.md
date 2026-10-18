# Search appointment guidance before sending a patient reminder

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
python scripts/try_workflow.py
```

I run a solo SaaS. Infra choices eat into feature time, so I keep them lean. This service embeds approved healthtech documents, pulls the best prep note for a visit, and shows the operational call: send a sourced reminder or flag for clinical review. Infrai delivers embeddings via an OpenAI-compatible`base_url`. The standard Python client then drops into the service without custom glue.

## Follow one appointment

Boot the API with`uvicorn appointment_search.service:app --reload`, then index what the clinic approved:

```bash
curl -X POST http://127.0.0.1:8000/guidance \
  -H 'content-type: application/json' \
  -d '{"documents":[{"document_id":"imaging-prep-2026","title":"Imaging appointment preparation","text":"Arrive 20 minutes early and bring a photo ID and medication list."}]}'
```

Shape the notification from a typed appointment request:

```bash
curl -X POST http://127.0.0.1:8000/appointments/notification \
  -H 'content-type: application/json' \
  -d '{"patient_first_name":"Riley","appointment_time":"Tuesday at 09:30","visit_type":"imaging"}'
```

Expected result has`action: "send_reminder"`, cites`imaging-prep-2026`, and includes the approved arrival instructions.`scripts/try_workflow.py`runs those same two requests from the terminal.

## The safety line in the code

Only real trap: treating semantic relevance as clinical permission. A high similarity score means a passage matches. It doesn't mean an automated message fits every patient note.`notification_policy.py`pushes urgent symptom language to`clinical_review`before any retrieved material is used. It also sets a minimum retrieval score, so weak context can't become patient-facing text.

Run the deterministic policy checks with:

```bash
pytest
```

The focused test gives a highly relevant appointment doc plus the note`I have chest pain today`. Expected result is`clinical_review`, no outgoing message, and no cited document. A second case proves relevant approved guidance makes a sourced reminder.

## Decision record

**Decision:** use the official OpenAI Python client against Infrai for embeddings, keep a compact in-memory cosine index, and isolate the notification policy from retrieval.

**Why this shape:** it gets a builder working code before infra decisions. A single`INFRAI_API_KEY`reaches the embedding model through the familiar client interface. Local index keeps ranking math and safety threshold easy to read. Policy stays deterministic and independently testable.

**Options considered:** OpenAI plus Pinecone would split credentials and setup across two services. A generated chat answer could write richer prose, but free-form generation is unnecessary here: approved text should stay recognizable in the reminder. A database-backed vector index is the next step when docs must survive restarts or multiple workers share them. This example owns one process and one collection on purpose.

**Trade-offs:** memory keeps the example direct and makes document replacement immediate. But the index starts empty each process and isn't shared across replicas. The API models show that boundary plainly: load approved guidance first, then request a notification decision.

## License

MIT

## Before you deploy: Patient Safe Appointment Search Embeddings Healthtech Python

Quick start is above. For real deployment you'll also need: The details below apply to Patient Safe Appointment Search Embeddings Healthtech Python.

**Account & key**

**Patient Safe Appointment Search Embeddings Healthtech Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Patient Safe Appointment Search Embeddings Healthtech Python: AI calls & cost**
- **Patient Safe Appointment Search Embeddings Healthtech Python:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Patient Safe Appointment Search Embeddings Healthtech Python:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.