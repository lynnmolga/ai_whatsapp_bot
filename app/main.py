from fastapi import FastAPI
from pydantic import BaseModel

from app.ai_answer import generate_draft
from app.storage import append_jsonl, now_iso
from app.config import DRAFTS_PATH


app = FastAPI(title="Busy But Alive")


class IncomingMessage(BaseModel):
    sender: str
    message: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/draft")
def create_draft(payload: IncomingMessage):
    result = generate_draft(
        sender=payload.sender,
        message=payload.message,
    )

    row = {
        "created_at": now_iso(),
        **result,
    }

    append_jsonl(DRAFTS_PATH, row)

    return row