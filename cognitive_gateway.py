"""Local opt-in HTTP facade for the existing Obsidia Cognitive Ingress.

Run separately: OBSIDIA_STUDIO_ENABLE_INGRESS=1 python cognitive_gateway.py
The Jarvis repository is imported, never edited. Default is disabled.
"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Obsidia Cognitive Ingress Gateway")
JARVIS = Path(os.getenv("OBSIDIA_JARVIS_ROOT", str(Path.home() / "Desktop" / "obsidia-jarvis-advanced-integration-v0"))).resolve()


class Request(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    session_id: str = "obsidia-studio"
    allow_local_model: bool = False


@app.get("/health")
def health():
    return {"enabled": os.getenv("OBSIDIA_STUDIO_ENABLE_INGRESS") == "1",
            "source_exists": (JARVIS / "scripts" / "obsidia_cognitive_ingress_v0.py").is_file(),
            "local_model_enabled": os.getenv("OBSIDIA_STUDIO_ENABLE_LOCAL_MODEL") == "1"}


@app.post("/api/cognitive/ingress")
def ingress(req: Request):
    if os.getenv("OBSIDIA_STUDIO_ENABLE_INGRESS") != "1":
        raise HTTPException(503, "Cognitive Ingress is disabled by default.")
    if not (JARVIS / "scripts" / "obsidia_cognitive_ingress_v0.py").is_file():
        raise HTTPException(503, "Cognitive Ingress source not found.")
    if req.allow_local_model and os.getenv("OBSIDIA_STUDIO_ENABLE_LOCAL_MODEL") != "1":
        raise HTTPException(403, "Local model invocation requires explicit gateway opt-in.")
    if str(JARVIS) not in sys.path:
        sys.path.insert(0, str(JARVIS))
    try:
        from scripts.obsidia_cognitive_ingress_v0 import run_cognitive_ingress
        result = run_cognitive_ingress(
            text=req.text,
            session_id=req.session_id,
            allow_local_model=bool(req.allow_local_model),
        )
    except Exception as exc:
        raise HTTPException(502, "Cognitive Ingress unavailable: " + type(exc).__name__) from exc
    if not isinstance(result, dict):
        raise HTTPException(502, "Cognitive Ingress returned a non-dictionary result.")
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8110)
